# Школски асистент

Мултимодални помоћник који ради **на самом уређају**: упериш камеру на радни
лист, електричну шему или мерни инструмент, поставиш питање гласом на српском, а
одговор се рачуна локално (визуелно-језички модел + опциони RAG над школским
материјалима) и изговара. Пројекат програма [Edge AI Пирот](https://edgeai.tsp.edu.rs).

Ни слика, ни глас, ни питања не одлазе на туђи сервер. Модели се преузму једном,
после тога систем ради офлајн.

## Хардвер

- NVIDIA Jetson Orin Nano Super Developer Kit (8 GB), активни хладњак, напајање 19 V
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

## Лиценца

MIT (`LICENSE`).
