# Паметна зебра

<!-- значке:почетак -->
![статус: предлог](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%BF%D1%80%D0%B5%D0%B4%D0%BB%D0%BE%D0%B3-2f6fed) ![платформа: Raspberry Pi 5](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Raspberry_Pi_5-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/pametna-zebra)
<!-- значке:крај -->

Камера изнад пешачког прелаза **локално** броји пешаке и возила и пали
светлосно упозорење када се пешак и возило приближавају истовремено.
Пројекат програма [Edge AI Пирот](https://edgeai.tsp.edu.rs).

**Приватност уграђена у дизајн:** не снима се слика ни видео. Памте се само
бројеви — колико пешака, колико возила, у ком временском интервалу (`brojac.csv`).

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 02 |
| **Статус** | предлог |
| **Платформа** | Raspberry Pi 5 |
| **Хардвер** | Raspberry Pi 5, AI HAT+ Hailo-8L, Camera Module 3 |
| **Технологије** | YOLOv8n, ByteTrack, LED упозорење |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/pametna-zebra) · [упутство](https://edgeai.tsp.edu.rs/uputstva/ai-hat-hailo) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

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

## Додатак: Хардверска надградња са сетом „37 у 1” 🚦

Када основни софтверски ланац проради у симулацији или са обичном камером, на Raspberry Pi 5 се могу везати модули из школског сензорског сета „37 у 1” за пуну физичку сигнализацију на макети пешачког прелаза:

1. **RGB LED модул (KY-016)** или **Двобојна LED (KY-011)** — динамички пешачки семафор:
   - 🟢 **Зелено:** Слободан прелаз (нема возила у зони прилаза).
   - 🟡 **Жуто:** Опрез (возило уочено у зони успоравања).
   - 🔴 **Црвено трепћуће:** Опасност (пешак ступио на прелаз + возило брзо прилази, $TTC < 3\,\text{s}$).
2. **Активна зујалица (Buzzer KY-012)** — испрекидани звучни аларм за пешаке и возаче у тренутку опасности.
3. **5V Релеј модул (KY-019)** — аутоматско укључивање јачег спољног LED рефлектора за осветљење прелаза ноћу.
4. **LDR фотоотпорник (KY-018)** — сензор амбијенталног светла: рефлектор преко релеја се активира само када падне мрак.

### Илустрација: Шема повезивања на Raspberry Pi 5 (40-pin GPIO)

```
        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power ────────► [VCC] 5V Релеј (KY-019)
               │ ●  ● │(Pin 4)  5V Power
   GND  (Pin 6)│ ●  ● │(Pin 5)
               │ ●  ● │(Pin 9)  GND ─────────────► [GND] Заједничка маса свих модула
GPIO 17 (Pin 11)│ ●  ● │(Pin 12)
GPIO 27 (Pin 13)│ ●  ● │(Pin 14)
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [S / IN] Активна зујалица (KY-012)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [IN] 5V Релеј (KY-019)
               │ ●  ● │(Pin 20) GND
GPIO 25 (Pin 22)│ ●  ● │(Pin 21)
               └──────────────┘

  Детаљна веза сигнала:
  ├── RGB LED (KY-016):
  │     ├── Pin 'R' (Црвена)   ──► GPIO 17  (Pin 11)
  │     ├── Pin 'G' (Зелена)   ──► GPIO 27  (Pin 13)
  │     ├── Pin 'B' (Плава)    ──► GPIO 22  (Pin 15)
  │     └── Pin '-' (GND)      ──► Заједнички GND (Pin 9 или 20)
  │
  ├── Активна зујалица (KY-012):
  │     ├── Pin 'S' (Сигнал)   ──► GPIO 23  (Pin 16)
  │     └── Pin '-' (GND)      ──► Заједнички GND
  │
  ├── 5V Релеј (KY-019):
  │     ├── Pin 'VCC'          ──► 5V  (Pin 2)
  │     ├── Pin 'GND'          ──► GND (Pin 6 или 20)
  │     └── Pin 'IN'           ──► GPIO 24  (Pin 18)
  │
  └── LDR сензор светла са компаратором (KY-018):
        ├── Pin 'VCC'          ──► 3.3V (Pin 1)  [ПАЖЊА: не на 5V због Pi 5 GPIO!]
        ├── Pin 'GND'          ──► GND
        └── Pin 'DO' (Digital) ──► GPIO 25  (Pin 22)
```

> [!WARNING]
> **Важно за Raspberry Pi 5:** Сви сигнални pin-ови раде искључиво на **3.3V логици**. LDR модул увек напајајте са 3.3V pina (Pin 1). Релеј модул користи 5V за напајање шпулне, али његов контролни улаз (IN) безбедно окида са 3.3V логичким нивоом.

### Пример кода за проширење (без мењања постојећег кода)

Ученици могу додати класу у `src/zebra/io/hardware_upgrade.py`:

```python
"""Проширена контрола хардвера из сета 37 у 1 за Паметну зебру."""
from __future__ import annotations
import logging

log = logging.getLogger(__name__)

class SmartZebraHardware:
    """Управља RGB семафором, зујалицом, LDR-ом и релејем за рефлектор."""

    def __init__(
        self,
        pin_r: int = 17,
        pin_g: int = 27,
        pin_b: int = 22,
        pin_buzzer: int = 23,
        pin_relay: int = 24,
        pin_ldr: int = 25,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._led = None
        self._buzzer = None
        self._relay = None
        self._ldr = None

        if not enabled:
            return

        try:
            from gpiozero import RGBLED, Buzzer, OutputDevice, DigitalInputDevice

            self._led = RGBLED(red=pin_r, green=pin_g, blue=pin_b, active_high=True)
            self._buzzer = Buzzer(pin_buzzer)
            self._relay = OutputDevice(pin_relay, active_high=True, initial_value=False)
            self._ldr = DigitalInputDevice(pin_ldr)

            log.info("Хардвер из сета 37 у 1 успешно иницијализован.")
            self.set_status("safe")
        except Exception as exc:
            log.warning("Хардвер недоступан (%s) — прелаз у софтверски симулатор.", exc)
            self.enabled = False

    def is_dark(self) -> bool:
        """Враћа True ако је LDR очитао низак ниво амбијенталног светла."""
        return bool(self._ldr and self._ldr.is_active)

    def set_status(self, level: str) -> None:
        """Поставља стање семафора: 'safe', 'caution', или 'danger'."""
        if not self.enabled:
            return

        # 1. Ноћни рефлектор преко релеја
        if self._relay:
            if self.is_dark() and level in ("caution", "danger"):
                self._relay.on()
            elif not self.is_dark():
                self._relay.off()

        # 2. Светлосна и звучна сигнализација
        if level == "danger":
            if self._led:
                self._led.color = (1, 0, 0)      # Црвено
            if self._buzzer:
                self._buzzer.beep(on_time=0.1, off_time=0.1)  # Испрекидани аларм
        elif level == "caution":
            if self._led:
                self._led.color = (1, 0.7, 0)    # Жуто
            if self._buzzer:
                self._buzzer.off()
        else:  # safe
            if self._led:
                self._led.color = (0, 1, 0)      # Зелено
            if self._buzzer:
                self._buzzer.off()

    def close(self) -> None:
        if self._led:
            self._led.close()
        if self._buzzer:
            self._buzzer.close()
        if self._relay:
            self._relay.close()
        if self._ldr:
            self._ldr.close()
```

### Брзи тест на плочи

Пре спајања са камером и модела, ученици могу тестирати повезивање:
```bash
python -c "
from gpiozero import RGBLED, Buzzer; import time
led = RGBLED(17, 27, 22); b = Buzzer(23)
print('Зелено...'); led.color = (0, 1, 0); time.sleep(1)
print('Жуто...'); led.color = (1, 0.7, 0); time.sleep(1)
print('Црвено + аларм...'); led.color = (1, 0, 0); b.beep(0.1, 0.1, n=5); time.sleep(1)
led.close(); b.close()
"
```

<!-- приватност:почетак -->
## Приватност и подаци

Камера гледа пешаке на прелазу; слика се не чува. Општа правила за податке ученика: [`docs/privatnost.md`](../../docs/privatnost.md). Овај пројекат још нема свој `docs/etika.md`.
<!-- приватност:крај -->

## Лиценца

MIT (`LICENSE`).

