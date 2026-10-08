# Примери за Raspberry Pi 5

Мале апликације са камером, ЛиДАР-ом и говором које прате лекције у **Учионици** на
сајту ([edgeai.tsp.edu.rs/lms](https://edgeai.tsp.edu.rs/lms)). Свака лекција има
своје примере, а свака страна примера на сајту води овде.

## Подешавање (једном)

```bash
sudo apt install python3-picamera2 espeak-ng python3-tk
cd ~/primeri
python3 -m venv --system-site-packages env     # --system-site-packages да се види picamera2
source env/bin/activate
pip install -r requirements.txt
```

## Покретање

```bash
cd ~/primeri
./pokreni.sh                    # прозор ако постоји екран, иначе текстуални мени
python pokretac.py --cli        # текстуални мени преко SSH-а
```

Или појединачно, на пример `cd ~/primeri/test && python check_cam.py`.
Детаљан списак пример по пример је у `pokretanje.txt`.

**Путања.** Покретач и `pokreni.sh` користе фолдер у коме се налазе (на Pi-ју `~/primeri`).
Ако желиш другачије, постави `PRIMERI_DIR`. Једино `AI_Primeri.desktop` садржи
апсолутну путању `/home/pi/primeri/pokreni.sh` — уреди је ако је фолдер на другом месту.

## Преглед

| фолдер | шта је | лекција |
|---|---|---|
| `uvod/` | NumPy и OpenCV на једној слици и са камером (раде и без Pi-ја) | Увод 3–4 |
| `test/` | провера камере (`check_cam.py`, `check_format.py`) и бројање прстију (`proba.py`) | 1, 2 |
| `igrice/` + `sortiranje/` | шест игара за предшколце и њихов покретач | 2 |
| `vozibezbedno/`, `klon/` | лице: умор, осећања, Матрикс/Тесла | 4 |
| `mesec/`, `pucketanje/`, `hemija/` | слој преко камере: месец, невидљивост, AR хемија | 5 |
| `kvo-te/` | КВО ТЕ, пиротски чет-бот (има свој `README.md`) | 3 |
| `lidar/` | радар за RPLIDAR (има свој `README.md`) | 6 |

## Најчешће грешке

* **`ModuleNotFoundError`** — окружење није активно (`source ~/primeri/env/bin/activate`).
* **`picamera2` се не учитава у окружењу** — окружење је направљено без `--system-site-packages`.
* **„Камера није пронађена“** — друга апликација је већ користи; затвори је. Примери понекад
  предлажу `libcamerify python …`.
* **Прозор се не појављује из SSH сесије** — примери постављају `DISPLAY=:0`; на Pi-ју мора бити
  прикључен екран.
* **`mediapipe` грешка при инсталацији** — потребна је верзија `0.10.14` (види `requirements.txt`).

## Лиценца и извори

Кôд је под MIT лиценцом (`../../LICENSE`). Материјал трећих страна и отворена питања
лиценце (речник, фотографије у `klon/`) су у `../../CREDITS.md`.
