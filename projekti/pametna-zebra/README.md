# Паметна зебра

Камера изнад пешачког прелаза **локално** броји пешаке и возила и пали
светлосно упозорење када се пешак и возило приближавају истовремено.
Пројекат програма [Edge AI Пирот](https://edgeai.tsp.edu.rs).

**Приватност уграђена у дизајн:** не снима се слика ни видео. Памте се само
бројеви — колико пешака, колико возила, у ком временском интервалу (`brojac.csv`).

## Хардвер

- Raspberry Pi 5 + AI HAT+ (Hailo-8L) — за инференцу у реалном времену
- Camera Module 3
- LED из сета „37 у 1" на GPIO 17

Ради и на обичном рачунару са веб камером (спорије, YOLO на процесору) —
за развој и учење.

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/pametna-zebra
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -e ".[yolo]"        # на Raspberry Pi додатно:  pip install -e ".[yolo,rpi]"
zebra download-model            # преузме yolov8n.pt (једном)
```

## Покретање

```bash
zebra run --sim --display        # симулација, без камере и без модела
zebra run --source 0 --display   # веб камера
zebra run --backend hailo        # на Pi са AI HAT+ (пада на YOLO ако Hailo није ту)
zebra calibrate                  # означи зоне прелаза и коловоза → zones.json
zebra devices                    # индекси камера
```

Тастери у прегледу: `Q`/`ESC` излаз.

## Како ради

```
камера ─► детекција (YOLOv8n: person + car/truck/bus/moto/bike)
            │
            ▼
      ByteTrack асоцијација  (двостепено: поуздане па слабе детекције)
            │  трагови са ID-јем и брзином
            ▼
    ┌───────┴────────┐
 бројач           правило упозорења
 (по типу,       пешак на прелазу + возило на коловозу
  по зони,       + време до судара (TTC) < праг
  CSV на 60 s)     │  хистерезис: држи упозорење још 2 s
                   ▼
              LED (GPIO) + банер на екрану
```

### Модули (`src/zebra/`)

| модул | шта ради | тестиран |
|---|---|---|
| `detect/` | YOLO / Hailo / dummy детектор | dummy |
| `track/bytetrack.py` | ByteTrack асоцијација + процена брзине | да |
| `safety/geometry.py` | време до судара (TTC), најмање растојање | да |
| `safety/zone.py` | полигони прелаза/коловоза, где је ко | да |
| `safety/policy.py` | правило упозорења + хистерезис | да |
| `io/counter.py` | бројање и CSV лог | да |
| `io/gpio_led.py` | LED упозорење (без хардвера — тихо ништа) | — |
| `app.py` | склапање целог ланца | sim |

Hailo backend (`detect/hailo_backend.py`) има место за попуну на радионици
(учитавање HEF модела); док није попуњено, аутоматски користи YOLO на процесору.

## Тестови

```bash
pip install -e ".[dev]"
pytest
```

## Лиценца

MIT (`LICENSE`).
