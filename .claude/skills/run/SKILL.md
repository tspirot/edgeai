---
name: run
description: Launch the Edge AI site (web/) or any of the 5 student Edge AI projects (titlovi-uzivo, cuvar-stare-planine, pametna-zebra, kontrola-kvaliteta, znakovna-azbuka) locally or in simulation mode. Use when asked to run, start, test, preview, or screenshot apps in this repo.
---

# Покретање апликација и пројеката у репоу

## 1. Сајт (`web/`)

```bash
cd web
npm install        # само први пут
npm run dev        # http://localhost:5173 (или наредни слободан порт)
```

- HMR укључен — измене се виде одмах.
- Продукциони билд: `npm run build` → `web/dist/`; преглед: `npm run preview` (:4173).
- Тема: памти се у `localStorage ('edgeai-theme')`. Прекидач теме у навигацији мења изглед одмах.

### Headless screenshot сајта (са 3D сценом)

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --use-gl=angle --use-angle=swiftshader \
  --enable-unsafe-swiftshader --window-size=1600,1000 \
  --virtual-time-budget=9000 --screenshot=out.png http://localhost:5173/
```

---

## 2. Ученички Edge AI пројекти (`projekti/`)

Сваки пројекат ради и на развојном рачунару (Windows/Linux/macOS) у симулационом режиму (`--sim` или `--backend dummy`), без камере, сензора или AI HAT-а.

### Пројекат 01: Титлови уживо (`projekti/titlovi-uzivo/`)
Препознавање говора на српском кроз Whisper модел локално:
```bash
cd projekti/titlovi-uzivo
python -m venv .venv && source .venv/Scripts/activate
pip install -e .

titlovi run --backend dummy --console   # брза проба без микрофона
titlovi devices                         # листа аудио улаза
titlovi download-model --model base     # преузми модел (једном)
titlovi run                             # пуни рад са прозором
```

### Пројекат 02: Паметна зебра (`projekti/pametna-zebra/`)
Детекција пешака и возила, праћење брзине и упозорење на судар:
```bash
cd projekti/pametna-zebra
python -m venv .venv && source .venv/Scripts/activate
pip install -e ".[yolo]"
zebra download-model                    # преузми yolov8n.pt (једном)

zebra run --sim --display               # симулација без камере
zebra run --source 0 --display          # веб камера са екраном
zebra calibrate                         # калибрација зона прелаза
```

### Пројекат 03: Чувар Старе планине (`projekti/cuvar-stare-planine/`)
AI фотозамка која класификује дивљач и бележи климу и квалитет ваздуха:
```bash
cd projekti/cuvar-stare-planine
python -m venv .venv && source .venv/Scripts/activate
pip install -e ".[onnx]"

cuvar run --sim                         # симулација са синтетичким догађајима
cuvar run --source 0                    # веб камера са dummy класификацијом
cuvar gallery                           # преглед сачуваних догађаја
cuvar power --triggers-per-hour 4       # прорачун трајања батерије
```

### Пројекат 04: Контрола квалитета (`projekti/kontrola-kvaliteta/`)
Визуелна детекција аномалија узорака учена само на исправним комадима:
```bash
cd projekti/kontrola-kvaliteta
python -m venv .venv && source .venv/Scripts/activate
pip install -e .

qc sim                                  # симулација на вештачким узорцима
qc fit uzorci/ok --val uzorci/val       # обука меморије исправних комада
qc check slika.jpg                      # провера једне слике (код 1 = аномалија)
qc eval test/                           # провера тачности и одзива
```

### Пројекат 05: Знаковна азбука (`projekti/znakovna-azbuka/`)
Препознавање слова српске једноручне азбуке из 21 тачке шаке:
```bash
cd projekti/znakovna-azbuka
python -m venv .venv && source .venv/Scripts/activate
pip install -e ".[hands]"

znak sim                                # симулација ланца препознавања
znak record --label A -n 60             # снимање скупа узорака за слово
znak train                              # обука k-NN модела (podaci.csv -> model.npz)
znak run                                # препознавање уживо преко камере
```
