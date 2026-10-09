# Знаковна азбука

<!-- значке:почетак -->
![статус: предлог](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%BF%D1%80%D0%B5%D0%B4%D0%BB%D0%BE%D0%B3-2f6fed) ![платформа: Raspberry Pi 5](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Raspberry_Pi_5-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/znakovna-azbuka)
<!-- значке:крај -->

Препознавање слова **српске једноручне азбуке** из положаја шаке — локално на
Raspberry Pi-ју, из тачака шаке. Пројекат програма
[Edge AI Пирот](https://edgeai.tsp.edu.rs).

Језгро радионице: **ученици сами снимају и анотирају свој скуп података**
(`znak record` → CSV, по потреби Label Studio), па поново тренирају и гледају
како тачност расте.

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 05 |
| **Статус** | предлог |
| **Платформа** | Raspberry Pi 5 |
| **Хардвер** | Raspberry Pi 5, AI Camera IMX500 |
| **Технологије** | детекција тачака шаке, сопствени скуп података, Label Studio |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/znakovna-azbuka) · [упутство](https://edgeai.tsp.edu.rs/uputstva/ai-camera-imx500) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

## Хардвер

- Raspberry Pi 5 + Raspberry Pi AI Camera (IMX500) или Camera Module 3
- Екран/пројектор за исписано слово

Ради и на обичном рачунару са веб камером.

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/znakovna-azbuka
python -m venv .venv && source .venv/bin/activate
pip install -e ".[hands]"     # mediapipe за тачке шаке
```

## Употреба

```bash
znak sim                       # синтетички узорци — цео ланац без камере
znak record --label A -n 60    # сними 60 узорака за слово А (SPACE снима)
znak record --label B -n 60
znak train                     # podaci.csv → model.npz
znak run                       # препознавање уживо
```

## Како ради

```
камера ─► MediaPipe Hands: 21 тачка шаке
            │
     нормализација: зглоб у центар, скала по длану, ротација на „горе"
            │  → 42 броја, независно од положаја руке у кадру
            ▼
     k-НН класификатор  (научен на снимцима ученика)
            │  слово + поузданост
            ▼
     временско гласање: слово се исписује тек кад се потврди
            кроз више кадрова (не „поскакује")
```

### Модули (`src/znak/`)

| модул | шта ради | тестиран |
|---|---|---|
| `normalize.py` | нормализација тачака шаке (инваријантно) | да |
| `classifier.py` | k-НН + save/load | да |
| `vote.py` | временско гласање | да |
| `dataset.py` | CSV снимака (сирове тачке) + учитавање | да |
| `poses.py` | синтетички положаји за неколико слова | — |
| `hands/` | MediaPipe · dummy | dummy |
| `app.py` | склапање целог ланца | sim |

Синтетички се препознаје ~8 слова; пуна азбука има 30 — то се добија
снимањем правих података. Слова са покретом (нпр. Ж, Ћ) траже низ кадрова
уместо једног — природан наставак пројекта.

## Тестови

```bash
pip install -e ".[dev]" && pytest
```

<!-- приватност:почетак -->
## Приватност и подаци

Скуп података чине снимци шака ученика: сагласност је обавезна, а чувају се само тачке шаке. Општа правила за податке ученика: [`docs/privatnost.md`](../../docs/privatnost.md). Овај пројекат још нема свој `docs/etika.md`.
<!-- приватност:крај -->

## Лиценца

MIT (`LICENSE`).
