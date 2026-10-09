# Титлови уживо, без облака

<!-- значке:почетак -->
![статус: у изради](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D1%83_%D0%B8%D0%B7%D1%80%D0%B0%D0%B4%D0%B8-f0ad4e) ![платформа: Raspberry Pi 5](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Raspberry_Pi_5-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/titlovi-uzivo)
<!-- значке:крај -->

Препознавање говора на српском које ради **на самом уређају** и исписује титлове
у реалном времену — за ученике оштећеног слуха. Пројекат програма
[Edge AI Пирот](https://edgeai.tsp.edu.rs).

Звук се нигде не снима нити шаље. Модел се преузме једном, после тога систем
ради потпуно офлајн.

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 01 |
| **Статус** | у изради |
| **Платформа** | Raspberry Pi 5 |
| **Хардвер** | Raspberry Pi 5, USB микрофон, HDMI пројекција |
| **Технологије** | faster-whisper, LocalAgreement стриминг, пресловљавање |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/titlovi-uzivo) · [упутство](https://edgeai.tsp.edu.rs/uputstva/titlovi-uzivo-instalacija) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

## Хардвер

- Raspberry Pi 5 (8 GB), активни хладњак, напајање 27 W
- USB камера са микрофоном (или засебан USB микрофон)
- HDMI пројектор или монитор

Ради и на обичном рачунару (Windows/Linux/Mac) за развој и пробу.

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/titlovi-uzivo
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .
```

Модел (једном, уз интернет):

```bash
titlovi download-model --model base
```

## Покретање

```bash
titlovi devices                       # који је микрофон
titlovi run                           # титлови преко целог екрана (HDMI)
titlovi run --display web             # приказ у прегледачу, http://<ip>:8080
titlovi run --backend dummy --console # проба без микрофона и без модела
titlovi run --script latin            # латиница уместо ћирилице
titlovi run --wav snimak.wav          # из фајла уместо микрофона
```

Тастери у pygame приказу: `ESC`/`Q` излаз, `F` цео екран.

## Како ради

```
микрофон ──► детектор говора (VAD) ──► Whisper (faster-whisper, int8)
                                          │  сваких ~1.5 s на растућем прозору
                                          ▼
                            LocalAgreement: реч је потврђена кад се
                            појави у две узастопне хипотезе
                                          │
                     пресловљавање ◄──────┘
                          │
                          ▼
              приказ: pygame (HDMI) / web (LAN) / console
```

Потврђен текст је бео, несигуран „реп" сив.

### ASR backend-и

| backend | за шта | напомена |
|---|---|---|
| `faster-whisper` | **српски**, подразумевано | вишејезични Whisper модел, ради офлајн |
| `vosk` | други језици на радионицама | нема званичан модел за српски (08.09.2026) |
| `dummy` | проба и тестови | исписује унапред задат текст |

## Конфигурација

Види `config.example.yaml`. Покретање: `titlovi run -c config.yaml`.

## Тестови

```bash
pip install -e ".[dev]"
pytest
```

<!-- приватност:почетак -->
## Приватност и подаци

Говор ученика обрађује се само на уређају и не снима се. Општа правила за податке ученика: [`docs/privatnost.md`](../../docs/privatnost.md). Овај пројекат још нема свој `docs/etika.md`.
<!-- приватност:крај -->

## Лиценца

MIT (`LICENSE`).
