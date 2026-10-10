# Контрола квалитета без примера грешке

<!-- значке:почетак -->
![статус: предлог](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%BF%D1%80%D0%B5%D0%B4%D0%BB%D0%BE%D0%B3-2f6fed) ![платформа: Raspberry Pi 5](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Raspberry_Pi_5-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/kontrola-kvaliteta)
<!-- значке:крај -->

Визуелна контрола гумених и текстилних узорака кроз **детекцију аномалија**.
Модел се тренира **само на исправним комадима** и пријављује све што одступа —
рупу, ману у ткању, страно тело. Пројекат програма
[Edge AI Пирот](https://edgeai.tsp.edu.rs).

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 04 |
| **Статус** | предлог |
| **Платформа** | Raspberry Pi 5 |
| **Хардвер** | Raspberry Pi 5, AI HAT+ Hailo-8L, Camera Module 3 |
| **Технологије** | PatchCore / PaDiM, контролисано осветљење |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/kontrola-kvaliteta) · [упутство](https://edgeai.tsp.edu.rs/uputstva/ai-hat-hailo) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

## Зашто аномалије, а не класификација

- Шкартова никад нема довољно за тренинг класификатора; исправних има колико хоћеш.
- То је приступ који се стварно користи у индустрији.
- Ученици уче да раде са неуравнотеженим подацима.

## Хардвер

- Raspberry Pi 5 (+ AI HAT+ за јачи екстрактор обележја)
- Camera Module 3
- Контролисано осветљење (кутија, дифузор) — најважнији део поставке

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/kontrola-kvaliteta
python -m venv .venv && source .venv/bin/activate
pip install -e .            # torch екстрактор:  pip install -e ".[torch]"
```

## Употреба

```bash
qc sim                              # синтетички узорци: научи и оцени (без фајлова)
qc fit uzorci/ok --val uzorci/val   # научи из фасцикле исправних → model.npz
qc check slika.jpg                  # провери једну слику (izlazni kôd 1 = мана)
qc eval test/                       # test/ok/* и test/defect/* → одзив и лажни аларми
```

## Како ради (PatchCore-идеја)

```
слика ─► обележја по блоку  (G×G мрежа; светлина, текстура, ивице)
           handcrafted (Pi) · CNN (torch) · dummy
           │
   учење:  сви блокови исправних → „меморија"
   праг:   mean + k·std резултата на исправном валидационом скупу
           │
провера ─► за сваки блок: растојање до најближег у меморији
           резултат слике = максимум по блоковима
           топлотна мапа = резултат по блоковима → локализација мане
```

### Модули (`src/qc/`)

| модул | шта ради | тестиран |
|---|---|---|
| `features/handcrafted.py` | обележја по блоку без тешких библиотека | да |
| `features/torch_backend.py` | обележја из ResNet-18 (опционо) | — |
| `bank.py` | меморија + k-НН резултат + greedy coreset | да |
| `calibrate.py` | праг из резултата исправних | да |
| `detect.py` | цео детектор + топлотна мапа + save/load | да |
| `data.py` | учитавање фасцикли + синтетички узорци | — |
| `app.py` | обука и оцена | да |

## Тестови

```bash
pip install -e ".[dev]" && pytest
```

## Додатак: Хардверска надградња са сетом „37 у 1” 🏭

У индустријском окружењу (попут пиротске гумарске или текстилне производње), визуелна инспекција захтева синхронизацију са траком и тренутну физичку реакцију на дефект. Софтвер се проширује модулима из сета „37 у 1”:

1. **Оптички прекидач са прорезом (Photo-interrupter KY-010)** или **TCRT5000 (KY-033)**:
   - Хардверски окидач камере: када узорак прође кроз оптички сноп на покретној траци, камера слика тачно центриран кадар без кашњења.
2. **5V Релеј модул (KY-019)** — **Избацивач шкарта:**
   - Када PatchCore/PaDiM модел детектује аномалију (скор изнад прага), релеј окида електромагнетни потискивач или преусмеривач који неисправан комад одваја са траке.
3. **RGB LED (KY-016)** или **Двобојна LED (KY-011)** — **Индустријски Andon стуб:**
   - 🟢 **Зелено:** Исправан комад (OK).
   - 🔴 **Црвено:** Откривен дефект / Шкарт (Defect).
4. **Активна зујалица (Buzzer KY-012)**:
   - Кратак звучни сигнал упозорења за контролора квалитета приликом одбацивања шкарта.
5. **Ротациони енкодер са тастером (KY-040)** — **Физичко подешавање прага:**
   - Окретањем точкића оператер у реалном времену подешава праг осетљивости детекције ($k$ вредност у `calibrate.py`), а притиском на тастер покреће брзо учење на нову серију исправних узорака.

---

### Илустрација: Шема повезивања на Raspberry Pi 5 (40-pin GPIO)

```
        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power ────────► [VCC] 5V Релеј (KY-019)
               │ ●  ● │(Pin 4)  5V Power
   GND  (Pin 6)│ ●  ● │(Pin 5)
               │ ●  ● │(Pin 9)  GND ─────────────► [GND] Заједничка маса свих модула
GPIO 17 (Pin 11)│ ●  ● │(Pin 12) GPIO 18 ────────► [CLK] Ротациони енкодер (KY-040)
GPIO 27 (Pin 13)│ ●  ● │(Pin 14) GND
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [DT]  Ротациони енкодер (KY-040)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [SW]  Енкодер тастер    (KY-040)
               │ ●  ● │(Pin 20) GND
GPIO 25 (Pin 22)│ ●  ● │(Pin 21)
               └──────────────┘

  Детаљна веза сигнала:
  ├── Оптички окидач камере (KY-010 / TCRT5000):
  │     ├── OUT (Digital) ─────► GPIO 17 (Pin 11)
  │     ├── VCC ───────────────► 3.3V (Pin 1)
  │     └── GND ───────────────► GND (Pin 6 или 9)
  │
  ├── 5V Релеј за избацивање шкарта (KY-019):
  │     ├── IN ────────────────► GPIO 27 (Pin 13)
  │     ├── VCC ───────────────► 5V  (Pin 2)
  │     └── GND ───────────────► GND
  │
  ├── Активна зујалица (KY-012):
  │     ├── S (Сигнал) ────────► GPIO 22 (Pin 15)
  │     └── - (GND)    ────────► GND
  │
  ├── Двобојна / RGB LED Andon индикација:
  │     ├── R (Црвена) ────────► GPIO 25 (Pin 22)
  │     ├── G (Зелена) ────────► GPIO 26 (Pin 37)
  │     └── GND ───────────────► GND (Pin 20)
  │
  └── Ротациони енкодер за праг (KY-040):
        ├── CLK ───────────────► GPIO 18 (Pin 12)
        ├── DT  ───────────────► GPIO 23 (Pin 16)
        ├── SW (Тастер) ───────► GPIO 24 (Pin 18)
        ├── VCC ───────────────► 3.3V
        └── GND ───────────────► GND
```

---

### Пример кода за проширење (без мењања постојећег кода)

Ученици могу креирати класу у `src/qc/hardware_upgrade.py`:

```python
"""Индустријска хардверска периферија из сета 37 у 1 за контролу квалитета."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class QualityControlHardware:
    """Управља оптичким окидачем, релејем за шкарт, Andon LED-ом и зујалицом."""

    def __init__(
        self,
        pin_trigger: int = 17,
        pin_relay: int = 27,
        pin_buzzer: int = 22,
        pin_led_ok: int = 26,
        pin_led_defect: int = 25,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._trigger = None
        self._relay = None
        self._buzzer = None
        self._led_ok = None
        self._led_defect = None

        if not enabled:
            return

        try:
            from gpiozero import DigitalInputDevice, OutputDevice, Buzzer, LED

            self._trigger = DigitalInputDevice(pin_trigger, pull_up=False)
            self._relay = OutputDevice(pin_relay, active_high=True, initial_value=False)
            self._buzzer = Buzzer(pin_buzzer)
            self._led_ok = LED(pin_led_ok)
            self._led_defect = LED(pin_led_defect)

            log.info("Индустријски контролер 37 у 1 иницијализован.")
            self.set_idle()
        except Exception as exc:
            log.warning("GPIO недоступан (%s) — софтверски симулатор.", exc)
            self.enabled = False

    def wait_for_part(self, timeout_s: float = 5.0) -> bool:
        """Чека да оптички сноп региструје узорак на позицији за снимање."""
        if not self.enabled or not self._trigger:
            time.sleep(0.5)
            return True
        return self._trigger.wait_for_active(timeout=timeout_s)

    def report_result(self, is_defect: bool) -> None:
        """Пријављује резултат инспекције на Andon индикаторима и релеју."""
        if not self.enabled:
            return

        if is_defect:
            if self._led_ok: self._led_ok.off()
            if self._led_defect: self._led_defect.on()
            if self._buzzer: self._buzzer.beep(on_time=0.1, off_time=0.1, n=2)
            # Активирање избацивача шкарта на 300 ms
            if self._relay:
                self._relay.on()
                time.sleep(0.3)
                self._relay.off()
            log.warning("ШКАРТ ОДБАЧЕН: Активиран пнеуматски релеј!")
        else:
            if self._led_defect: self._led_defect.off()
            if self._led_ok: self._led_ok.on()
            if self._buzzer: self._buzzer.off()

    def set_idle(self) -> None:
        if self._led_ok: self._led_ok.on()
        if self._led_defect: self._led_defect.off()
        if self._buzzer: self._buzzer.off()
        if self._relay: self._relay.off()

    def close(self) -> None:
        for dev in (self._trigger, self._relay, self._buzzer, self._led_ok, self._led_defect):
            if dev: dev.close()
```

### Брзи тест на плочи

```bash
python -c "
from gpiozero import OutputDevice, Buzzer, LED; import time
relay = OutputDevice(27); b = Buzzer(22); led_ok = LED(26); led_bad = LED(25)
print('Исправан комад (OK): зелено...'); led_ok.on(); led_bad.off(); time.sleep(1)
print('Шкарт (Defect): црвено + зујалица + релеј...');
led_ok.off(); led_bad.on(); b.beep(0.1, 0.1, n=2); relay.on(); time.sleep(0.3); relay.off()
time.sleep(1); led_bad.off(); b.close(); relay.close(); led_ok.close(); led_bad.close()
"
```

## Лиценца

MIT (`LICENSE`).
