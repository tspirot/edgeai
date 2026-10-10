# Усправно

<!-- значке:почетак -->
![статус: предлог](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%BF%D1%80%D0%B5%D0%B4%D0%BB%D0%BE%D0%B3-2f6fed) ![платформа: Raspberry Pi 5](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Raspberry_Pi_5-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/uspravno)
<!-- значке:крај -->

Камера са стране прати држање ученика за столом. Локално (само тачке тела, слика
се **не** снима) рачуна угао врата и трупа, мери колико времена по часу протекне
у лошем положају и благо подсећа на исправљање. Пројекат програма
[Edge AI Пирот](https://edgeai.tsp.edu.rs).

> **Ово је алат за освешћивање навике држања, не медицински уређај.** Не
> поставља дијагнозу — ни скалиозе ни кифозе. Упорна одступања → школски лекар.

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 09 |
| **Статус** | предлог |
| **Платформа** | Raspberry Pi 5 |
| **Хардвер** | Raspberry Pi 5, Camera Module 3, LED / зујалица |
| **Технологије** | MediaPipe Pose, углови из кључних тачака, лична калибрација |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/uspravno) · [упутство](https://edgeai.tsp.edu.rs/uputstva/uspravno-postavka) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

## Хардвер

- Raspberry Pi 5 (8 GB), активни хладњак
- Camera Module 3 (или USB веб камера), са стране, у висини рамена
- LED из сета „37 у 1“ или мала зујалица на GPIO 17
- 3D штампан држач камере за поновљив угао

Без хардвера ради у симулацији: `drzanje sim`.

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/uspravno
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # језгро: симулација, тестови

pip install -e ".[kamera,poza]"  # камера (OpenCV) + MediaPipe Pose
pip install -e ".[rpi]"          # GPIO подсетник, Picamera2
```

## Ток рада

```bash
drzanje sim                       # цео ланац без камере и модела
drzanje calibrate                 # седи усправно ~5 s → лична референца
drzanje run                       # надзор уживо; на крају уписује сесију
drzanje run --seconds 2700        # један школски час
drzanje report                    # сажетак свих сесија
drzanje report --screening        # извештај асиметрије (ако је укључен режим)
```

## Како ради

```
камера ──► MediaPipe Pose (33 тачке тела)
                    │
        углови: врат (уво–раме) и труп (раме–кук) у односу на вертикалу
                    │
        одступање од личне референце  →  праг + хистереза + тајмер
                    │
    погрбљеност дуже од N s  →  LED / зујалица;  бројеви  →  drzanje.csv
```

### Заменљиви модули

| корак | подразумевано | алтернативе |
|---|---|---|
| камера | `auto` (Picamera2 → OpenCV) | `dummy` |
| поза | `mediapipe` | `dummy` (синтетички скелет) |
| подсетник | `auto` (GPIO → терминал) | `console`, `none` |

## Приватност

- Слика се нигде не снима нити приказује.
- Из кадра се извуку само 33 тачке скелета; у меморији остају накратко.
- На диск иду **само бројеви**: углови, минути погрбљености, број епизода
  (`drzanje.csv`). Ништа по чему се особа препознаје.

## „Скрининг“ режим (опционо)

Поглед спреда: `screening.enabled: true`. Кроз недеље бележи просечан нагиб
линије рамена и кукова (`skrining.csv`). `drzanje report --screening` прави
сажетак и **обележи** доследна одступања — да их човек погледа. Систем ништа не
тврди; извештај се носи школском лекару.

## Тестови

```bash
pip install -e ".[dev]"
pytest
```

## Додатак: Хардверска надградња са сетом „37 у 1” 🪑

Да подсетник не би био агресиван и да би се лакше користио током целог школског часа, на сто се поставља физичка конзола са модулима из сета „37 у 1”:

1. **RGB LED модул (KY-016)** — **Амбијентално светло на столу:**
   - 🟢 **Зелено / Плаво:** Правилно, усправно држање тела.
   - 🟡 **Жуто:** Почетак погрбљености (< 15 s) — благо визуелно упозорење на рубу видног поља.
   - 🔴 **Црвено:** Упорна погрбљеност (> 30 s) — јасан позив на исправљање.
2. **Пасивна зујалица (KY-006)** — **Дискретни акустични подсетник:**
   - Уместо оштрог пиштања, пасивна зујалица свира тих, нискотонски подсетник са постепеним успоном тона само ако црвена фаза потраје преко прага.
3. **Тактилни тастер (KY-004)** — **Тастер за брзу рекалибрацију:**
   - Ученик седне правилно за сто и притисне тастер на кућишту — систем моментално узима референтне углове без куцања команди у конзоли.
4. **Сензор нагиба (KY-020) или вибрације (KY-002)**:
   - Монтиран на наслон столице: детектује да ли је ученик заиста за столом или је устао (спречава лажне аларме када је столица празна).

---

### Илустрација: Шема повезивања на Raspberry Pi 5 (40-pin GPIO)

```
        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power
               │ ●  ● │(Pin 6)  GND ─────────────► [GND] Заједничка маса
GPIO 17 (Pin 11)│ ●  ● │(Pin 12)
GPIO 27 (Pin 13)│ ●  ● │(Pin 14) GND
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [S]   Калибрациони тастер (KY-004)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [S]   Пасивна зујалица    (KY-006)
               │ ●  ● │(Pin 20) GND
GPIO 25 (Pin 22)│ ●  ● │(Pin 21)
               └──────────────┘

  Детаљна веза сигнала:
  ├── RGB LED амбијентални индикатор (KY-016):
  │     ├── R (Црвена) ────────► GPIO 17 (Pin 11)
  │     ├── G (Зелена) ────────► GPIO 27 (Pin 13)
  │     ├── B (Плава)  ────────► GPIO 22 (Pin 15)
  │     └── - (GND)    ────────► GND (Pin 6 или 14)
  │
  ├── Калибрациони тастер на столу (KY-004):
  │     ├── S (Сигнал) ────────► GPIO 23 (Pin 16)
  │     ├── VCC ───────────────► 3.3V (Pin 1 или 17)
  │     └── GND ───────────────► GND
  │
  └── Пасивна зујалица за благи тон (KY-006):
        ├── S (Сигнал PWM) ────► GPIO 24 (Pin 18)
        └── - (GND)    ────────► GND (Pin 20)
```

---

### Пример кода за проширење (без мењања постојећег кода)

Ученици могу креирати класу у `src/drzanje/hardware_upgrade.py`:

```python
"""Амбијентални хардверски подсетник из сета 37 у 1 за пројекат Усправно."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class DeskReminderHardware:
    """Управља амбијенталним RGB светлом, тихом зујалицом и тастером на столу."""

    def __init__(
        self,
        pin_r: int = 17,
        pin_g: int = 27,
        pin_b: int = 22,
        pin_btn: int = 23,
        pin_buzzer: int = 24,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._led = None
        self._btn = None
        self._buzzer = None

        if not enabled:
            return

        try:
            from gpiozero import RGBLED, Button, TonalBuzzer

            self._led = RGBLED(red=pin_r, green=pin_g, blue=pin_b)
            self._btn = Button(pin_btn, pull_up=True)
            self._buzzer = TonalBuzzer(pin_buzzer)

            log.info("Хардвер за праћење држања иницијализован.")
            self.set_posture("good")
        except Exception as exc:
            log.warning("GPIO недоступан (%s) — конзолни подсетник.", exc)
            self.enabled = False

    def is_calibrate_pressed(self) -> bool:
        """Враћа True ако ученик притиска тастер за рекалибрацију седења."""
        return bool(self._btn and self._btn.is_pressed)

    def set_posture(self, status: str) -> None:
        """Поставља амбијентално светло: 'good', 'warning' или 'slouch'."""
        if not self.enabled:
            return

        if status == "good":
            if self._led: self._led.color = (0, 0.4, 0.8)  # Смирујућа плава/зелена
            if self._buzzer: self._buzzer.stop()
        elif status == "warning":
            if self._led: self._led.color = (0.9, 0.5, 0)  # Топла жута
            if self._buzzer: self._buzzer.stop()
        elif status == "slouch":
            if self._led: self._led.color = (1, 0, 0)      # Црвена
            if self._buzzer:
                try:
                    self._buzzer.play("A4")                # Благи подсетник (440 Hz)
                    time.sleep(0.15)
                    self._buzzer.stop()
                except Exception:
                    pass

    def close(self) -> None:
        for dev in (self._led, self._btn, self._buzzer):
            if dev: dev.close()
```

### Брзи тест на плочи

```bash
python -c "
from gpiozero import RGBLED, Button; import time
led = RGBLED(17, 27, 22); btn = Button(23)
print('Усправно: плава LED...'); led.color = (0, 0.5, 1); time.sleep(1)
print('Погрбљено: црвена LED...'); led.color = (1, 0, 0); time.sleep(1)
print('Седни усправно и притисни тастер за калибрацију (GPIO 23)...')
btn.wait_for_press(timeout=5)
print('Калибрација потврђена!'); led.color = (0, 1, 0); time.sleep(1)
led.close(); btn.close()
"
```

<!-- приватност:почетак -->
## Приватност и подаци

Рачуна се само из тачака тела; слика се не снима. Етика: `docs/uglovi-i-etika.md`. Општа правила за податке ученика: [`docs/privatnost.md`](../../docs/privatnost.md).
<!-- приватност:крај -->

## Лиценца

MIT (`LICENSE`).
