# Спој исте сличице

![ниво: основно](https://img.shields.io/badge/%D0%BD%D0%B8%D0%B2%D0%BE-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE-2f6fed) ![хардвер: Camera Module 3](https://img.shields.io/badge/%D1%85%D0%B0%D1%80%D0%B4%D0%B2%D0%B5%D1%80-Camera_Module_3-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab)

Игра за предшколце: сличице се хватају штипањем у ваздуху и спуштају у кућицу са истом сликом.

![Спој исте сличице — приказ уживо](/slike/primeri/sortiranje.jpg)

## Покретање

```bash
cd ~/primeri/sortiranje
python sortiranje.py
```

## Како ради

- Пет тема нивоа: облици и небо, животиње, воће, играчке и возила, бројање балона.
- У кућицама су сенке сличица, па дете одмах види где која припада.
- Покреће се из покретача игрица (`../igrice/pokretac_igrice.py`) или директно.

## Додатак: Хардверска надградња са сетом „37 у 1” 🏭🧩

Игра се може претворити у мини-макету индустријске сортне станице додавањем физичких актуатора из сета „37 у 1”:

1. **5V Релеј (KY-019) на GPIO 24** — **Сортна капија:**
   - Када дете тачно спусти сличицу у кућицу, релеј одапиње резу/капију уз јасан механички „клик” (симулација сортирања на правој траци).
2. **RGB LED (KY-016) на GPIO 22 (R), 27 (G), 23 (B)**:
   - 🟢 **Зелено:** Тачно спојена сличица.
   - 🔴 **Црвено:** Погрешна кућица (пробај поново).
3. **Пасивна зујалица (KY-006) на GPIO 25**:
   - Кратак мелодијски тон похвале при завршетку нивоа.

```
                  Raspberry Pi 5 GPIO Pinout (Сортирање)
                         ┌──────────────┐
       3.3V Power (Pin 1)│ ●  ● │(Pin 2)  5V Power ───────► [VCC] 5V Релеј (KY-019)
                         │ ●  ● │(Pin 4)  5V Power
       GND        (Pin 6)│ ●  ● │(Pin 5)
                         │ ●  ● │(Pin 9)  GND ────────────► [GND] Заједничка маса
                         │ ●  ● │(Pin 14) GND ────────────► [GND] RGB LED (KY-016)
  [G] Зелена     (Pin 13)│ ●  ● │(Pin 16) GPIO 23 ───────► [B] Плава LED  (KY-016)
  [R] Црвена     (Pin 15)│ ●  ● │(Pin 18) GPIO 24 ───────► [IN] 5V Релеј   (KY-019)
                         │ ●  ● │(Pin 20) GND ────────────► [GND] 5V Релеј  (KY-019)
                         │ ●  ● │(Pin 22) GPIO 25 ───────► [S] Зујалица    (KY-006)
                         └──────────────┘
```

### Пример проширења у Python-у

```python
from gpiozero import RGBLED, OutputDevice, TonalBuzzer

led = RGBLED(red=22, green=27, blue=23)
relay = OutputDevice(24)
buzzer = TonalBuzzer(25)

def on_correct_sort():
    led.color = (0, 1, 0)
    relay.on()
    buzzer.play("C5")
    time.sleep(0.15)
    relay.off()
    buzzer.stop()
    led.off()
```

### Брзи тест на плочи

```bash
python -c "
from gpiozero import RGBLED, OutputDevice; import time
led = RGBLED(22, 27, 23); relay = OutputDevice(24)
print('Тачно: зелена LED + релеј капија...'); led.color = (0, 1, 0); relay.on(); time.sleep(0.3); relay.off(); led.off()
print('Нетачно: црвена LED...'); led.color = (1, 0, 0); time.sleep(0.5); led.off()
led.close(); relay.close()
"
```

## Лекција и сајт

Прати лекцију: [Лекција 2: Руке, лице и покрет](https://edgeai.tsp.edu.rs/lms/ruke-i-pokret) · [Лекција 7: Edge AI среће физички свет](https://edgeai.tsp.edu.rs/lms/ai-i-fizicki-svet)
Страница примера на сајту: [Спој исте сличице](https://edgeai.tsp.edu.rs/lms/primeri/sortiranje)

Окружење и зависности: [`../README.md`](../README.md) · [`../requirements.txt`](../requirements.txt).
