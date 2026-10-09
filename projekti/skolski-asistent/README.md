# Школски асистент

<!-- значке:почетак -->
![статус: предлог](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%BF%D1%80%D0%B5%D0%B4%D0%BB%D0%BE%D0%B3-2f6fed) ![платформа: NVIDIA Jetson Orin Nano](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-NVIDIA_Jetson_Orin_Nano-76b900) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/skolski-asistent)
<!-- значке:крај -->

Мултимодални помоћник који ради **на самом уређају**: упериш камеру на радни
лист, електричну шему или мерни инструмент, поставиш питање гласом на српском, а
одговор се рачуна локално (визуелно-језички модел + опциони RAG над школским
материјалима) и изговара. Пројекат програма [Edge AI Пирот](https://edgeai.tsp.edu.rs).

Ни слика, ни глас, ни питања не одлазе на туђи сервер. Модели се преузму једном,
после тога систем ради офлајн.

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 06 |
| **Статус** | предлог |
| **Платформа** | NVIDIA Jetson Orin Nano |
| **Хардвер** | Jetson Orin Nano (8 GB), Logitech C922, активни хладњак, NVMe SSD |
| **Технологије** | Qwen2-VL (VLM), faster-whisper, Piper TTS, RAG над материјалима |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/skolski-asistent) · [упутство](https://edgeai.tsp.edu.rs/uputstva/skolski-asistent-postavka) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

## Хардвер

- NVIDIA Jetson Orin Nano Developer Kit (8 GB), активни хладњак, напајање 19 V
  (уз JetPack 6.2 иста плоча ради у „Super“ режиму — до 67 TOPS)
- Logitech C922 Pro Stream (1080p, аутофокус, стерео микрофон)
- NVMe SSD за моделе и базу материјала
- Звучник или слушалице

Ради и на обичном рачунару за развој — на процесору спорије, или на GPU-у ако
га има. Без хардвера ради у `dummy` режиму (доле).

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/skolski-asistent
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # језгро: ланац са dummy модулима, тестови

# додаци по потреби:
pip install -e ".[kamera,zvuk]"  # камера (OpenCV) и микрофон (sounddevice)
pip install -e ".[asr]"          # faster-whisper (говор → текст)
pip install -e ".[vlm]"          # transformers + torch (Qwen2-VL)
pip install -e ".[tts]"          # piper-tts (говор на српском)
pip install -e ".[rag]"          # sentence-transformers (боља претрага)
```

Модели (једном, уз интернет):

```bash
asistent download-model --what all
```

## Покретање

```bash
asistent devices                                   # које су камере и микрофони
asistent run                                        # петља: Enter → питање → одговор
asistent ask --image sema.jpg --question "Шта је ово?"   # једно питање, без микрофона
asistent ask --vlm dummy --asr dummy --tts console --image sema.jpg \
             --question "Шта је ово?"               # цео ланац без модела и хардвера
```

RAG над школским материјалима:

```bash
asistent index build materijali/                    # .txt и .md → индекс
asistent index show                                 # шта је у индексу
asistent ask --rag --image zadatak.jpg --question "Помози ми са овим задатком"
```

## Како ради

```
камера (C922) ──► кадар (RGB)
микрофон ──► Whisper (faster-whisper) ──► текст питања
                                            │
                 RAG (опционо): top-k исечака из материјала ◄─┘
                                            │
                        Qwen2-VL (int4) ◄───┤  слика + питање + исечци
                                            ▼
                                   одговор на српском
                                            │
                                Piper TTS ──┴──► изговорено + исписано
```

### Модули (заменљиви)

| корак | подразумевано | алтернатива |
|---|---|---|
| ASR | `faster-whisper` (српски, офлајн) | `dummy` (задат текст) |
| VLM | `qwen` (Qwen2-VL-2B, int4) | `dummy` (опис слике + питања) |
| TTS | `piper` (глас `sr_RS-serbian-medium`) | `console` (испис у терминал) |
| RAG уградња | `hashing` (без зависности) | `sentence-transformers` |

## Конфигурација

Види `config.example.yaml`. Покретање: `asistent ask -c config.yaml …`.
На Jetson-у поставити `asr.whisper.device: cuda` и `vlm.device: auto`.

## Обазриво

Мали VLM повремено погреши. RAG му даје ослонац у уџбенику, а одговор увек
треба проверити. На Demo Day-у се мери колико пута погоди.

## Тестови

```bash
pip install -e ".[dev]"
pytest
```

Тестови покривају конфигурацију, дељење текста и претрагу (RAG), лажни VLM и
цео ланац са `dummy` модулима — без модела и без хардвера.

<!-- приватност:почетак -->
## Приватност и подаци

Асистент може да чује и види ученике: ништа се не снима ни шаље ван школе. Општа правила за податке ученика: [`docs/privatnost.md`](../../docs/privatnost.md). Овај пројекат још нема свој `docs/etika.md`.
<!-- приватност:крај -->

## Лиценца

MIT (`LICENSE`).
