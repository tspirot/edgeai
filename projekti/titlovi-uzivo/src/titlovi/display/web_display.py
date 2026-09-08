"""Приказ титлова у прегледачу преко локалног HTTP сервера (Server-Sent Events).

Raspberry Pi сервира страницу; отвори је на пројектору у режиму киоска или на
било ком уређају на локалној мрежи. И даље без облака — све иде преко LAN-а.
Само стандардна библиотека, без додатних пакета.
"""

from __future__ import annotations

import json
import logging
import queue
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from titlovi.display.base import Display

log = logging.getLogger(__name__)

_PAGE = """<!doctype html>
<html lang="sr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Титлови уживо</title>
<style>
  :root { color-scheme: dark; }
  * { box-sizing: border-box; margin: 0; }
  html, body { height: 100%; background: #000; }
  body {
    display: flex; align-items: flex-end; padding: 6vh 6vw;
    font-family: "Segoe UI", "Noto Sans", system-ui, sans-serif;
  }
  #t {
    width: 100%; font-size: 5.2vw; line-height: 1.3; font-weight: 600;
    color: #fff; text-shadow: 0 2px 12px rgba(0,0,0,.6);
    max-height: 46vh; overflow: hidden;
    display: flex; flex-direction: column; justify-content: flex-end;
  }
  #t .p { color: #8a8a8a; }
  #badge {
    position: fixed; top: 3vh; left: 6vw; font-size: 1.5vw; letter-spacing: .12em;
    color: #6a6a6a; text-transform: uppercase;
  }
  #off { position: fixed; top: 3vh; right: 6vw; font-size: 1.5vw; color: #c0392b; }
</style>
</head>
<body>
  <div id="badge">● локално · без облака</div>
  <div id="off" hidden>веза прекинута</div>
  <div id="t"><span id="c"></span> <span id="p" class="p"></span></div>
<script>
  const c = document.getElementById('c');
  const p = document.getElementById('p');
  const off = document.getElementById('off');
  function connect() {
    const es = new EventSource('/stream');
    es.onmessage = (e) => {
      off.hidden = true;
      const d = JSON.parse(e.data);
      c.textContent = d.committed || '';
      p.textContent = d.partial || '';
    };
    es.onerror = () => { off.hidden = false; es.close(); setTimeout(connect, 1500); };
  }
  connect();
</script>
</body>
</html>
"""


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):  # тишина
        pass

    def _send(self, body: bytes, content_type: str) -> None:
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        display: "WebDisplay" = self.server.display  # type: ignore[attr-defined]
        if self.path in ("/", "/index.html"):
            self._send(_PAGE.encode("utf-8"), "text/html; charset=utf-8")
            return
        if self.path != "/stream":
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.end_headers()

        sub = display._subscribe()
        try:
            while not display._stopped:
                try:
                    data = sub.get(timeout=15)
                except queue.Empty:
                    self.wfile.write(b": ping\n\n")
                    self.wfile.flush()
                    continue
                self.wfile.write(f"data: {data}\n\n".encode("utf-8"))
                self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass
        finally:
            display._unsubscribe(sub)


class WebDisplay(Display):
    def __init__(self, cfg) -> None:
        self.cfg = cfg
        self._subs: set[queue.Queue] = set()
        self._lock = threading.Lock()
        self._last = {"committed": "", "partial": ""}
        self._stopped = False
        self._server = None

    def start(self) -> None:
        self._server = ThreadingHTTPServer((self.cfg.host, self.cfg.port), _Handler)
        self._server.display = self  # type: ignore[attr-defined]
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        host = "localhost" if self.cfg.host in ("0.0.0.0", "") else self.cfg.host
        url = f"http://{host}:{self.cfg.port}/"
        log.info("Веб приказ титлова: %s", url)
        if self.cfg.open_browser:
            try:
                webbrowser.open(url)
            except Exception:  # pragma: no cover
                pass

    def _subscribe(self) -> queue.Queue:
        sub: queue.Queue = queue.Queue()
        with self._lock:
            self._subs.add(sub)
        sub.put(json.dumps(self._last))
        return sub

    def _unsubscribe(self, sub: queue.Queue) -> None:
        with self._lock:
            self._subs.discard(sub)

    def render(self, committed: str, partial: str) -> None:
        payload = {"committed": committed, "partial": partial}
        if payload == self._last:
            return
        self._last = payload
        data = json.dumps(payload)
        with self._lock:
            subs = list(self._subs)
        for sub in subs:
            sub.put(data)

    def should_quit(self) -> bool:
        return False

    def stop(self) -> None:
        self._stopped = True
        if self._server is not None:
            try:
                self._server.shutdown()
            except Exception:  # pragma: no cover
                pass
