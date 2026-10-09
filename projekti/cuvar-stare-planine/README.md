# Чувар Старе планине

<!-- значке:почетак -->
![статус: предлог](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%BF%D1%80%D0%B5%D0%B4%D0%BB%D0%BE%D0%B3-2f6fed) ![платформа: Raspberry Pi 5](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Raspberry_Pi_5-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/cuvar-stare-planine)
<!-- значке:крај -->

Фотозамка која **на самом уређају** препознаје животињску врсту и бележи
температуру, влажност и квалитет ваздуха. Без сигнала, без интернета,
рад на батерији. Пројекат програма [Edge AI Пирот](https://edgeai.tsp.edu.rs).

Снима се **само кадар у коме је нешто препознато** — картица траје данима,
батерија недељама.

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 03 |
| **Статус** | предлог |
| **Платформа** | Raspberry Pi 5 |
| **Хардвер** | Raspberry Pi 5, AI Camera IMX500, BME688 |
| **Технологије** | класификација врста, рад на батерији, инференца на сензору |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/cuvar-stare-planine) · [упутство](https://edgeai.tsp.edu.rs/uputstva/ai-camera-imx500) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

## Хардвер

- Raspberry Pi 5 + Raspberry Pi AI Camera (**IMX500** — мрежа ради на сензору)
- BME688 сензор гаса и климе (I²C)
- Пакет батерија (нпр. 3× 18650)

Ради и на обичном рачунару са веб камером — за развој и обуку модела.

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/cuvar-stare-planine
python -m venv .venv && source .venv/bin/activate
pip install -e ".[onnx]"          # на Pi:  pip install -e ".[onnx,rpi]"
```

## Покретање

```bash
cuvar run --sim                    # симулација, без камере и сензора
cuvar run --source 0              # веб камера, dummy класификатор ако нема модела
cuvar run --classify onnx        # свој ONNX класификатор врста (CPU)
cuvar power --triggers-per-hour 4 # процена трајања батерије
cuvar gallery                     # сажетак сачуваних догађаја
```

## Како ради

```
камера ─► окидач по покрету (разлика кадра / PIR)
             │ (уз cooldown, да не снима исту животињу 100×)
             ▼
      класификатор врсте  (IMX500 на сензору · ONNX на CPU · dummy)
             │ ако score ≥ праг
             ▼
   BME688: температура, влажност, притисак, гас → AQI
             │
             ▼
   складиште: 1 JPG + 1 JSON по догађају, ротација старих
```

### Модули (`src/cuvar/`)

| модул | шта ради | тестиран |
|---|---|---|
| `trigger.py` | окидач по покрету (разлика од научене позадине) | да |
| `power.py` | процена трајања батерије (duty-cycle) | да |
| `storage.py` | чување догађаја + ротација | да |
| `classify/` | IMX500 (стуб) · ONNX (CPU) · dummy | dummy |
| `climate/` | BME688 (I²C) · dummy; ом→AQI | да |
| `app.py` | склапање целог ланца | sim |

IMX500 backend има место за попуну на радионици (учитавање `.rpk` модела);
док није попуњено, сам пада на ONNX/dummy.

## Тестови

```bash
pip install -e ".[dev]" && pytest
```

## Лиценца

MIT (`LICENSE`).
