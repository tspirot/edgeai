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

## Додатак: Хардверска надградња са сетом „37 у 1” 🖐️

За интерактивну учионицу и рад са децом, систем препознавања знаковне азбуке се надграђује модулима из школског сета „37 у 1”:

1. **Тактилни тастер (KY-004)** — **Окидач за снимање узорака (Dataset Capture):**
   - Ученик држи руку у положају слова, а другом руком (или ножном педалом) притиска тастер за унос узорка у базу. Нема потребе за нагињањем ка тастатури и развлачењем тела из кадра.
2. **RGB LED модул (KY-016)** — **Визуелни фидбек у реалном времену:**
   - 🟡 **Жуто:** Рука уочена, временско гласање у току.
   - 🟢 **Зелено:** Слово успешно препознато и потврђено.
   - 🔴 **Црвено:** Непрепознат положај шаке.
3. **Пасивна зујалица (KY-006)** — **Акустични фидбек:**
   - Кратак пријатан тон када се слово успешно потврди, чиме се добија мултисензорно искуство учења знаковног језика.
4. **Ротациони енкодер (KY-040)** — **Бирач слова:**
   - Окретањем точкића на инсталацији бира се циљно слово за учење (од А до Ш) без потребе за куцањем команди у терминалу.

---

### Илустрација: Шема повезивања на Raspberry Pi 5 (40-pin GPIO)

```
        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power
               │ ●  ● │(Pin 6)  GND ─────────────► [GND] Заједничка маса
GPIO 17 (Pin 11)│ ●  ● │(Pin 12) GPIO 18 ────────► [CLK] Енкодер бирач (KY-040)
GPIO 27 (Pin 13)│ ●  ● │(Pin 16) GPIO 23 ────────► [DT]  Енкодер бирач (KY-040)
GPIO 22 (Pin 15)│ ●  ● │(Pin 18) GPIO 24 ────────► [SW]  Енкодер тастер (KY-040)
               │ ●  ● │(Pin 22) GPIO 25 ────────► [S]   Пасивна зујалица (KY-006)
GPIO 26 (Pin 37)│ ●  ● │(Pin 36) GPIO 16 ────────► [S]   Тастер за узорке (KY-004)
               └──────────────┘

  Детаљна веза сигнала:
  ├── Тастер за снимање узорка (KY-004):
  │     ├── S (Сигнал) ────────► GPIO 16 (Pin 36)
  │     ├── VCC ───────────────► 3.3V (Pin 1)
  │     └── GND ───────────────► GND (Pin 6 или 14)
  │
  ├── RGB LED визуелни фидбек (KY-016):
  │     ├── R (Црвена) ────────► GPIO 17 (Pin 11)
  │     ├── G (Зелена) ────────► GPIO 27 (Pin 13)
  │     ├── B (Плава)  ────────► GPIO 22 (Pin 15)
  │     └── - (GND)    ────────► GND
  │
  ├── Пасивна зујалица за тонове (KY-006):
  │     ├── S (Сигнал PWM) ────► GPIO 25 (Pin 22)
  │     └── - (GND)    ────────► GND
  │
  └── Ротациони енкодер (KY-040):
        ├── CLK ───────────────► GPIO 18 (Pin 12)
        ├── DT  ───────────────► GPIO 23 (Pin 16)
        ├── SW (Потврда) ──────► GPIO 24 (Pin 18)
        ├── VCC ───────────────► 3.3V
        └── GND ───────────────► GND
```

---

### Пример кода за проширење (без мењања постојећег кода)

Ученици могу креирати класу у `src/znak/hardware_upgrade.py`:

```python
"""Хардверски фидбек из сета 37 у 1 за Знаковну азбуку."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class SignLanguageFeedback:
    """Управља тастером за снимање, RGB статусом и звучним фидбеком."""

    def __init__(
        self,
        pin_btn: int = 16,
        pin_r: int = 17,
        pin_g: int = 27,
        pin_b: int = 22,
        pin_buzzer: int = 25,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._btn = None
        self._led = None
        self._buzzer = None

        if not enabled:
            return

        try:
            from gpiozero import Button, RGBLED, TonalBuzzer

            self._btn = Button(pin_btn, pull_up=True)
            self._led = RGBLED(red=pin_r, green=pin_g, blue=pin_b)
            self._buzzer = TonalBuzzer(pin_buzzer)

            log.info("Хардвер за знаковну азбуку иницијализован.")
            self.set_waiting()
        except Exception as exc:
            log.warning("GPIO недоступан (%s) — софтверски режим.", exc)
            self.enabled = False

    def is_record_pressed(self) -> bool:
        """Враћа True ако ученик притиска физички тастер за унос узорка."""
        return bool(self._btn and self._btn.is_pressed)

    def set_waiting(self) -> None:
        if self._led: self._led.color = (0.2, 0.2, 0)  # Блага жута

    def set_recognized(self, note: str = "C5") -> None:
        """Потврда: зелено светло + кратак мелодијски тон."""
        if not self.enabled: return
        if self._led: self._led.color = (0, 1, 0)
        if self._buzzer:
            try:
                self._buzzer.play(note)
                time.sleep(0.12)
                self._buzzer.stop()
            except Exception:
                pass

    def set_unknown(self) -> None:
        if self._led: self._led.color = (1, 0, 0)  # Црвено

    def close(self) -> None:
        for dev in (self._btn, self._led, self._buzzer):
            if dev: dev.close()
```

### Брзи тест на плочи

```bash
python -c "
from gpiozero import Button, RGBLED; import time
btn = Button(16); led = RGBLED(17, 27, 22)
print('Држи руку у кадру. Притисни тастер (KY-004) на GPIO 16 за снимање...')
led.color = (1, 1, 0)
btn.wait_for_press(timeout=5)
print('Тастер притиснут! Узорак снимљен.')
led.color = (0, 1, 0); time.sleep(1)
led.close(); btn.close()
"
```

<!-- приватност:почетак -->
## Приватност и подаци

Скуп података чине снимци шака ученика: сагласност је обавезна, а чувају се само тачке шаке. Општа правила за податке ученика: [`docs/privatnost.md`](../../docs/privatnost.md). Овај пројекат још нема свој `docs/etika.md`.
<!-- приватност:крај -->

## Лиценца

MIT (`LICENSE`).
