---
name: run
description: Launch the Edge AI site (web/) or the Титлови уживо app (projekti/titlovi-uzivo) locally. Use when asked to run, start, preview, or screenshot either app in this repo.
---

# Покретање апликација у репоу

## Сајт (`web/`)

```bash
cd web
npm install        # само први пут
npm run dev        # http://localhost:5173  (мрежа: http://<IP>:5173)
```

- HMR укључен — измене се виде одмах.
- Продукциони билд: `npm run build` → `web/dist/`; преглед: `npm run preview` (:4173).
- Из VS Code: **Run and Debug → „Сајт: Chrome + dev сервер“** (покреће и dev task).

### Screenshot без праве машине (headless)

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --use-gl=angle --use-angle=swiftshader \
  --enable-unsafe-swiftshader --window-size=1600,1000 \
  --virtual-time-budget=9000 --screenshot=out.png http://localhost:5173/
```

`--use-angle=swiftshader` је обавезан да WebGL (3D сцена) ради у headless режиму.
Ако сцена изостане на једном покушају (WebGL init је повремено спор), понови.

## Титлови уживо (`projekti/titlovi-uzivo/`)

```bash
cd projekti/titlovi-uzivo
python -m venv .venv && source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -e .

titlovi run --backend dummy --console   # проба без микрофона и без модела
titlovi devices                         # листа аудио улаза
titlovi download-model --model base     # једном, уз интернет
titlovi run                             # уживо, титлови преко екрана
```

- Из VS Code: **Run and Debug → „Титлови: демо (dummy, конзола)“**.
- Циљна платформа је Raspberry Pi 5; на Windows/Linux ради за развој и пробу.
