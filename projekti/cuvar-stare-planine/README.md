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

## Додатак: Хардверска надградња са сетом „37 у 1” 🌲

У основном режиму фотозамка се ослања на софтверску детекцију промене кадра. У теренским условима Старе планине, где је трајање батерије кључно, уређај се може надградити сензорима из школског сета „37 у 1”:

1. **IR сензор препрека / покрета (KY-032 или TCRT5000 KY-033)** — **Хардверски Wake-up окидач:**
   - Камера и NPU не троше струју непрекидном обрадом празног кадра.
   - Када животиња пресече инфрацрвени сноп на стази, GPIO сигнал тренутно буди камеру за снимање и класификацију.
2. **Сензор вибрације / ударца (KY-002 или KY-031) и нагиба (KY-020)** — **„Tamper” заштита:**
   - Региструје ако ветар, пад гране или медвед/дивља свиња удари или помери кућиште фотозамке.
   - У JSON метаподацима догађаја бележи се упозорење о физичком померању.
3. **DS18B20 дигитална температурна сонда (1-Wire)**:
   - Спољно мерење температуре земљишта или снега уз интерни BME688 сензор унутар кућишта.
4. **RGB LED модул (KY-016)** — **Теренска дијагностика са тајмаутом:**
   - Приликом везивања на дрво приказује статус: плаво (подизање), зелено (SD картица и сензори спремни), црвено (грешка).
   - Након 60 секунди аутоматски се гаси како светлост не би отерала ноћне животиње.

---

### Илустрација: Шема повезивања на Raspberry Pi 5 (40-pin GPIO)

```
        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power
GPIO 2  (Pin 3)│ ●  ● │(Pin 4)  5V Power
GPIO 3  (Pin 5)│ ●  ● │(Pin 6)  GND ─────────────► [GND] Заједничка маса свих сензора
GPIO 4  (Pin 7)│ ●  ● │(Pin 8)
   GND  (Pin 9)│ ●  ● │(Pin 10)
GPIO 17 (Pin 11)│ ●  ● │(Pin 12) GPIO 18
GPIO 27 (Pin 13)│ ●  ● │(Pin 14) GND
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [G] RGB LED Зелена (KY-016)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [B] RGB LED Плава  (KY-016)
               │ ●  ● │(Pin 20) GND
               └──────────────┘

  Детаљна веза сигнала:
  ├── BME688 клима/гас (I²C):
  │     ├── SDA ───────────────► GPIO 2 (Pin 3)
  │     ├── SCL ───────────────► GPIO 3 (Pin 5)
  │     ├── 3.3V ──────────────► Pin 1
  │     └── GND ───────────────► Pin 6
  │
  ├── IR Wake-up сензор (KY-032 / TCRT5000):
  │     ├── OUT (Digital) ─────► GPIO 17 (Pin 11)
  │     ├── VCC ───────────────► 3.3V (Pin 1 или Pin 17)
  │     └── GND ───────────────► GND
  │
  ├── Сензор ударца / вибрације (KY-002 / KY-031):
  │     ├── S (Сигнал) ────────► GPIO 27 (Pin 13)
  │     ├── VCC ───────────────► 3.3V
  │     └── GND ───────────────► GND
  │
  ├── DS18B20 температурна сонда (1-Wire):
  │     ├── DQ (Подаци) ───────► GPIO 4 (Pin 7) + 4.7kΩ pull-up отпорник на 3.3V
  │     ├── VDD ───────────────► 3.3V
  │     └── GND ───────────────► GND
  │
  └── RGB LED дијагностика (KY-016):
        ├── R (Црвена) ────────► GPIO 22 (Pin 15)
        ├── G (Зелена) ────────► GPIO 23 (Pin 16)
        ├── B (Плава)  ────────► GPIO 24 (Pin 18)
        └── - (GND)    ────────► GND (Pin 20)
```

> [!TIP]
> **Штедња батерије у шуми:** IR сензор троши мање од 15 mA. Коришћењем хардверског прекида (`gpiozero.Button` или `edge_detection`) систем може држати камеру у режиму ниске потрошње све док сноп није пресечен.

---

### Пример кода за проширење (без мењања постојећег кода)

Ученици могу додати класу у `src/cuvar/hardware_upgrade.py`:

```python
"""Хардверски сензори из сета 37 у 1 за фотозамку Чувар Старе планине."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class FieldHardware:
    """Управља IR окидачем, сензором вибрације и дијагностичком LED диодом."""

    def __init__(
        self,
        pin_ir: int = 17,
        pin_shock: int = 27,
        pin_led_r: int = 22,
        pin_led_g: int = 23,
        pin_led_b: int = 24,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._ir = None
        self._shock = None
        self._led = None
        self.tamper_detected = False

        if not enabled:
            return

        try:
            from gpiozero import DigitalInputDevice, RGBLED

            self._ir = DigitalInputDevice(pin_ir, pull_up=False)
            self._shock = DigitalInputDevice(pin_shock, pull_up=True)
            self._led = RGBLED(red=pin_led_r, green=pin_led_g, blue=pin_led_b)

            # Када се детектује ударац/померање кућишта
            self._shock.when_activated = self._on_tamper

            log.info("Теренски хардвер успешно покренут.")
            self.indicate_ready()
        except Exception as exc:
            log.warning("Теренски GPIO недоступан (%s) — рад без сензора из сета.", exc)
            self.enabled = False

    def _on_tamper(self) -> None:
        self.tamper_detected = True
        log.warning("ТАМПЕР АЛАРМ: Регистрован јак ударац или померање фотозамке!")

    def wait_for_motion(self, timeout_s: float = 10.0) -> bool:
        """Чека физички пролазак дивљачи испред IR сензора."""
        if not self.enabled or not self._ir:
            time.sleep(1)
            return True  # у симулацији увек враћа True
        return self._ir.wait_for_active(timeout=timeout_s)

    def indicate_ready(self) -> None:
        """Кратка зелена индикација да је све спремно, па гашење светла."""
        if self._led:
            self._led.color = (0, 1, 0)  # Зелено
            time.sleep(2.0)
            self._led.off()              # Гаси светло да не плаши животиње

    def close(self) -> None:
        if self._led:
            self._led.close()
        if self._ir:
            self._ir.close()
        if self._shock:
            self._shock.close()
```

### Брзи тест на плочи

```bash
python -c "
from gpiozero import DigitalInputDevice, RGBLED; import time
led = RGBLED(22, 23, 24)
ir = DigitalInputDevice(17)
print('Дијагностика: плава LED...'); led.color = (0, 0, 1); time.sleep(1)
print('Спремно: зелена LED...'); led.color = (0, 1, 0); time.sleep(1)
led.off()
print('Пређи руком испред IR сензора (KY-032 / TCRT5000)...')
if ir.wait_for_active(timeout=5):
    print('Сноп пресечен! Окидање успешно.')
else:
    print('Време истекло (нема покрета).')
led.close(); ir.close()
"
```

## Лиценца

MIT (`LICENSE`).
