# Титлови уживо, без облака

Препознавање говора на српском које ради **на самом уређају** и исписује титлове
у реалном времену — за ученике оштећеног слуха. Пројекат програма
[Edge AI Пирот](https://edgeai.tsp.edu.rs).

Звук се нигде не снима нити шаље. Модел се преузме једном, после тога систем
ради потпуно офлајн.

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

## Лиценца

MIT (`LICENSE`).
