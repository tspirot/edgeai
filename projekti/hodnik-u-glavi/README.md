# Ходник у глави

<!-- значке:почетак -->
![статус: предлог](https://img.shields.io/badge/%D1%81%D1%82%D0%B0%D1%82%D1%83%D1%81-%D0%BF%D1%80%D0%B5%D0%B4%D0%BB%D0%BE%D0%B3-2f6fed) ![платформа: Raspberry Pi 4](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B0-Raspberry_Pi_4-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![лиценца: MIT](https://img.shields.io/badge/%D0%BB%D0%B8%D1%86%D0%B5%D0%BD%D1%86%D0%B0-MIT-2ea44f) [![Страница на сајту](https://img.shields.io/badge/сајт-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs/projekti/hodnik-u-glavi)
<!-- значке:крај -->

2D SLAM једним ласерским сензором. Возило провоза простор, поравнава сваки нови
скен на већ виђено (ICP), из тог поравнања рачуна колико се померило и попуњава
occupancy grid. Кад мапа постоји, задаш тачку — A* нађе пут, pure pursuit га
прати. Све класични алгоритми, све на самом уређају. Пројекат програма
[Edge AI Пирот](https://edgeai.tsp.edu.rs).

Пар са пројектом „Ђак за воланом“: иста платформа, друга способност — тамо
возило прати научену стазу, овде разуме простор који први пут види.

<!-- преглед:почетак -->
## Преглед

| | |
|---|---|
| **Програм** | Edge AI Пирот · пројекат 08 |
| **Статус** | предлог |
| **Платформа** | Raspberry Pi 4 |
| **Хардвер** | RPLIDAR A1, PiRacer шасија, Raspberry Pi 4 |
| **Технологије** | scan-matching SLAM (ICP), occupancy grid, A* планирање, pure pursuit |
| **На сајту** | [страница пројекта](https://edgeai.tsp.edu.rs/projekti/hodnik-u-glavi) · [упутство](https://edgeai.tsp.edu.rs/uputstva/hodnik-u-glavi-slam) |
| **Тестови** | `pytest` у овом фолдеру |
<!-- преглед:крај -->

## Хардвер

- Slamtec RPLIDAR A1 (360°, до 12 m, ~5.5 Hz) на USB
- PiRacer шасија са пројекта „Ђак за воланом“ (или колица за гурање)
- Raspberry Pi 4 (4 GB) + активно хлађење
- Раван под, зидови (RPLIDAR не види стакло)

Без хардвера ради у симулацији: `mapa sim`.

## Инсталација

```bash
git clone https://github.com/tspirot/edgeai.git
cd edgeai/projekti/hodnik-u-glavi
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e .                 # језгро: симулација, тестови

pip install -e ".[lidar,pwm]"    # на возилу
```

## Ток рада

```bash
mapa sim                                   # синтетичка соба: мапирање + навигација
mapa sim --goal 2.0 1.0 --out out/s.png

mapa map --seconds 90 --out out/skola.npz  # 1) провези/гурни возило, сними мапу
mapa show out/skola.npz                     #    погледај мапу
mapa plan out/skola.npz --start 0 0 --goal 3 -1   # 2) испланирај пут по мапи
mapa navigate --goal 3 -1                    # 3) SLAM уживо + вожња до тачке
```

## Како ради

```
RPLIDAR скен (угао, растојање)
        │  поларно → тачке у равни
        ▼
   ICP: поравнај нови скен на последњих N скенова (у светском оквиру)
        │  из поравнања: колико се возило померило и заокренуло
        ▼
   Occupancy grid: за сваки зрак Брезенхам линија
        пут = слободно (−), погођена тачка = заузето (+), log-odds
        ▼
   A*: најкраћи низ слободних ћелија до циља (препреке проширене за возило)
        ▼
   Pure pursuit: тачка на путу испред возила → угао волана и брзина
```

### Модули (сваки има тест)

| фајл | шта ради |
|---|---|
| `icp.py` | поравнање два облака тачака (Kabsch у 2D) |
| `grid.py` | occupancy grid, log-odds, Брезенхам зраци |
| `planner.py` | проширење препрека + A* |
| `pursuit.py` | pure pursuit контролер |
| `slam.py` | скен → положај + мапа (scan-to-map ICP, модел константне брзине) |
| `world.py` | синтетичка соба и симулирани лидар (за `sim` и тестове) |

## Границе (важно за очекивања)

- **Без одометрије** — померај се рачуна само из скенова, па возило мора да иде
  **споро** (RPLIDAR A1 = 5–6 обртаја/с; на брзини се скен „размаже“).
- Scan-to-map поравнање **дрифтује** на дугим путањама без затварања петље. За
  ходник и просторију је довољно; велика зграда би тражила pose-graph SLAM.
- RPLIDAR не види стакло, огледала и танке ноге столица.

## Тестови

```bash
pip install -e ".[dev]"
pytest
```

Покривају ICP (померање, ротација), occupancy grid (зраци, засићење), A*
(обилажење, нема пута), pure pursuit, и цео SLAM ланац у симулацији.

## Лиценца

MIT (`LICENSE`).
