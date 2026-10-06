#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                    КВО ТЕ — ПИРОТСКИ AI МОЗАК (WEB SERVER)
================================================================================
Локални веб сервер са богатим интерфејсом за Windows, RPi 5 и друге системе.
Ради са стандардном Python библиотеком (без додатних pip инсталација).
Покреће се на http://localhost:8080
================================================================================
"""

import os
import sys
import json
import urllib.parse
import webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler
from socketserver import ThreadingMixIn
from pathlib import Path

# Осигурај правилан UTF-8 испис на конзоли
for stream in (sys.stdout, sys.stderr):
    reconfigure = getattr(stream, "reconfigure", None)
    if reconfigure is not None:
        try:
            reconfigure(encoding="utf-8")
        except Exception:
            pass

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

from pirotski_mozak import PirotskiMozak, PIROTSKI_RECNIK
from model_pirotskog_govora import ModelPirotskogGovora

mozak = PirotskiMozak()
model_govora = ModelPirotskogGovora()


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class KvoTeHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        if path == "/api/status":
            self._send_json({
                "status": "online",
                "naziv": "Кво Те — Пиротски AI Мозак",
                "broj_odrednica_sanu": model_govora.broj_odrednica,
                "os": sys.platform,
            })
            return

        if path == "/api/random_rec":
            if model_govora.odrednice:
                odr = random_choice = None
                import random
                odr = random.choice(model_govora.odrednice)
                self._send_json({
                    "rec": odr.get("rec", ""),
                    "vrsta": odr.get("vrsta", ""),
                    "znacenje": odr.get("znacenje", ""),
                    "primeri": odr.get("primeri", [])[:3],
                    "izvor": "САНУ речник"
                })
            else:
                import random
                rec, znacenje = random.choice(list(PIROTSKI_RECNIK.items()))
                self._send_json({
                    "rec": rec,
                    "vrsta": "дијалектизам",
                    "znacenje": znacenje,
                    "primeri": [],
                    "izvor": "Основни речник"
                })
            return

        if path == "/api/recnik":
            q = query.get("q", [""])[0].strip()
            rezultati = []
            if q:
                # Прво по пиротској речи
                rezultati = model_govora.nadji_pirotsku_rec(q)
                # Ако нема, пробај по српском појму
                if not rezultati:
                    rezultati = model_govora.nadji_srpski_pojam(q)
            else:
                # Врати првих 25 за преглед
                rezultati = model_govora.odrednice[:25]

            self._send_json({
                "upit": q,
                "ukupno": len(rezultati),
                "rezultati": rezultati[:50]
            })
            return

        if path == "/api/config":
            masked = ""
            if mozak.api_key:
                masked = mozak.api_key[:4] + "..." + mozak.api_key[-4:] if len(mozak.api_key) > 8 else "***"
            self._send_json({
                "provider": mozak.ai_provider,
                "model": mozak.llm_model,
                "has_api_key": bool(mozak.api_key),
                "masked_key": masked
            })
            return

        if path in ["/chat", "/chat/"]:
            self.path = "/chat.html"

        # За остале статичке фајлове (HTML, CSS, JS, слике)
        super().do_GET()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            data = json.loads(body.decode("utf-8"))
        except Exception:
            data = {}

        if path == "/api/config":
            provider = data.get("provider", "oflajn")
            api_key = data.get("api_key", "")
            model = data.get("model", "")
            if not api_key and mozak.api_key and data.get("keep_existing_key", True):
                api_key = mozak.api_key
            mozak.sacuvaj_konfiguraciju(provider, api_key, model)
            self._send_json({"uspeh": True, "provider": mozak.ai_provider, "model": mozak.llm_model})
            return

        if path == "/api/test_llm":
            rez = mozak.testiraj_llm()
            self._send_json(rez)
            return

        if path == "/api/chat":
            messages = data.get("messages", [])
            persona = data.get("persona", "stedisa")
            
            rez = mozak.obradi_razgovor(messages, persona=persona)

            if data.get("govori_na_serveru", False):
                mozak.govori(rez.get("odgovor", ""))

            self._send_json(rez)
            return

        if path == "/api/pitaj":
            pitanje = data.get("pitanje", "").strip()
            odgovor = mozak.obradi_pitanje(pitanje)
            namera = mozak.prepoznaj_nameru(pitanje)
            
            # Ако је тражен глас преко сервера
            if data.get("govori_na_serveru", False):
                mozak.govori(odgovor)

            self._send_json({
                "pitanje": pitanje,
                "odgovor": odgovor,
                "namera": namera
            })
            return

        if path == "/api/govori":
            tekst = data.get("tekst", "").strip()
            if tekst:
                mozak.govori(tekst)
            self._send_json({"uspeh": True})
            return

        self.send_error(404, "Endpoint not found")

    def _send_json(self, data: dict, status: int = 200):
        telo = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(telo)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(telo)

    def log_message(self, format, *args):
        # Пригуши сувишне HTTP лог поруке
        pass


def pokreni_server(port: int = 8080, otvori_browser: bool = True):
    server = ThreadedHTTPServer(("0.0.0.0", port), KvoTeHandler)
    url = f"http://localhost:{port}"
    print("=" * 70)
    print("      К В О   Т Е   —   П И Р О Т С К И   А И   ( W E B )")
    print("=" * 70)
    print(f"  ВЕБ АПЛИКАЦИЈА ЈЕ ПОКРЕНУТА:")
    print(f"  👉  {url}")
    print(f"  База података: {model_govora.broj_odrednica} одредница САНУ речника")
    print("=" * 70)

    if otvori_browser:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nЗаустављам сервер...")
        server.server_close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="КВО ТЕ Web Сервер")
    parser.add_argument("--port", type=int, default=8080, help="Порт за веб сервер (стандардно 8080)")
    parser.add_argument("--no-browser", action="store_true", help="Не отварај аутоматски прегледач")
    args = parser.parse_args()

    pokreni_server(port=args.port, otvori_browser=not args.no_browser)
