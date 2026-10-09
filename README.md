# Edge AI: Наука у петој брзини

**Вештачка интелигенција која ради на самом уређају — без облака.**
Програм радионица Техничке школе Пирот: ученици и наставници праве уређаје који
препознају слику и говор локално, на Raspberry Pi 5 и Jetson Orin Nano.

[![сајт: edgeai.tsp.edu.rs](https://img.shields.io/badge/%D1%81%D0%B0%D1%98%D1%82-edgeai.tsp.edu.rs-0c6146)](https://edgeai.tsp.edu.rs) [![кôд: MIT](https://img.shields.io/badge/%D0%BA%C3%B4%D0%B4-MIT-2ea44f)](LICENSE) [![садржај: CC BY-SA 4.0](https://img.shields.io/badge/%D1%81%D0%B0%D0%B4%D1%80%D0%B6%D0%B0%D1%98-CC_BY--SA_4.0-2f6fed)](LICENSE-CONTENT) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab) ![платформе: Raspberry Pi 5 · Jetson Orin Nano](https://img.shields.io/badge/%D0%BF%D0%BB%D0%B0%D1%82%D1%84%D0%BE%D1%80%D0%BC%D0%B5-Raspberry_Pi_5_%C2%B7_Jetson_Orin_Nano-c51a4a) [![CI](https://github.com/tspirot/edgeai/actions/workflows/ci.yml/badge.svg)](https://github.com/tspirot/edgeai/actions/workflows/ci.yml)

**Сајт:** [edgeai.tsp.edu.rs](https://edgeai.tsp.edu.rs) · **Учионица:** [edgeai.tsp.edu.rs/lms](https://edgeai.tsp.edu.rs/lms) · **Пројекти:** [edgeai.tsp.edu.rs/projekti](https://edgeai.tsp.edu.rs/projekti)

---

## Зашто на уређају, а не у облаку

- **Приватност** — слика и звук не напуштају учионицу.
- **Без кашњења** — нема пута до сервера и назад.
- **Ради без интернета** — на терену, у сали, на прелазу код школе.
- **Јефтино у раду** — нема претплате ни трошка по упиту.

## Пројекти

Дванаест ученичких пројеката. Сваки је самосталан Python пакет са својим `README.md`,
`pyproject.toml`, тестовима и `config.example.yaml`.

| № | Пројекат | Платформа | Статус | О чему се ради |
|---|---|---|---|---|
| 01 | [**Титлови уживо, без облака**](projekti/titlovi-uzivo) | Raspberry Pi 5 | у изради | Препознавање говора на српском које ради на самом уређају и исписује титлове у реалном времену — за ученике оштећеног слуха. |
| 02 | [**Паметна зебра**](projekti/pametna-zebra) | Raspberry Pi 5 | предлог | Камера изнад пешачког прелаза броји пешаке, прати возила и пали упозорење када се пешак и возило приближавају истовремено. |
| 03 | [**Чувар Старе планине**](projekti/cuvar-stare-planine) | Raspberry Pi 5 | предлог | Фотозамка која на лицу места препознаје животињску врсту и бележи температуру, влажност и квалитет ваздуха — без сигнала и без интернета. |
| 04 | [**Контрола квалитета без примера грешке**](projekti/kontrola-kvaliteta) | Raspberry Pi 5 | предлог | Визуелна контрола гумених и текстилних узорака кроз детекцију аномалија — модел се тренира само на исправним комадима. |
| 05 | [**Знаковна азбука**](projekti/znakovna-azbuka) | Raspberry Pi 5 | предлог | Препознавање слова српске знаковне азбуке преко тачака шаке и временског класификатора покрета. |
| 06 | [**Школски асистент**](projekti/skolski-asistent) | Jetson Orin Nano | предлог | Упериш камеру на радни лист, шему или инструмент и питаш на српском — одговор се рачуна локално, на уређају, без облака. |
| 07 | [**Ђак за воланом**](projekti/djak-za-volanom) | Raspberry Pi 4 | предлог | Ауто у размери 1:10 сам вози по стази — камера држи траку, а RPLIDAR је независни сигурносни слој који кочи на препреку. |
| 08 | [**Ходник у глави**](projekti/hodnik-u-glavi) | Raspberry Pi 4 | предлог | Возило с једним ласерским сензором провоза ходник, у ходу нацрта 2D мапу и онда само нађе пут до задате тачке. |
| 09 | [**Усправно**](projekti/uspravno) | Raspberry Pi 5 | предлог | Камера са стране прати држање ученика за столом — угао врата и трупа, време погрбљености — и благо подсећа на исправљање. Само тачке тела, без слике. |
| 10 | [**Шара у духу пиротског ћилима**](projekti/pirotski-cilim) | Jetson Orin Nano | предлог | Камера препозна шару на ћилиму и објасни је, а дифузиони модел на самој плочи компонује нову — па је претвори у картон за ткање, за школски разбој. |
| 11 | [**Двојник**](projekti/dvojnik) | Jetson Orin Nano | предлог | Ставиш предмет на окретни сто, камера га обиђе у круг, Orin од силуета сложи 3D модел — и школски штампач одштампа копију. |
| 12 | [**Жива реч**](projekti/ziva-rec) | Jetson Orin Nano | предлог | Теренска станица која снима пиротски говор у кући говорника, транскрибује на лицу места и одмах даје да се исправи — без мреже. |

Детаљи, шеме и упутства по пројекту су на [сајту](https://edgeai.tsp.edu.rs/projekti).

## Учионица

Лекције и примери за почетнике: од прве слике са камере до препознавања руку, лица и ЛиДАР-а.
**Предзнање** (Python, NumPy, OpenCV, рад на Pi-ју) се може прескочити. Свака лекција има
вежбу (пример из [`lms/primeri`](lms/primeri)) и кратак квиз.

| | Лекција | Трајање |
|---|---|---|
| Увод 1 | [Окружење: Pi, SSH, venv](https://edgeai.tsp.edu.rs/lms/okruzenje-pi-ssh-venv) | 30 мин |
| Увод 2 | [Python за оне који већ програмирају](https://edgeai.tsp.edu.rs/lms/python-za-pocetnike) | 40 мин |
| Увод 3 | [NumPy и низови](https://edgeai.tsp.edu.rs/lms/numpy-i-nizovi) | 45 мин |
| Увод 4 | [OpenCV основе](https://edgeai.tsp.edu.rs/lms/opencv-osnove) | 50 мин |
| Лекција 1 | [Камера и слика](https://edgeai.tsp.edu.rs/lms/kamera-i-slika) | 30 мин |
| Лекција 2 | [Руке, лице и покрет](https://edgeai.tsp.edu.rs/lms/ruke-i-pokret) | 50 мин |
| Лекција 3 | [Разговор без облака](https://edgeai.tsp.edu.rs/lms/razgovor-bez-oblaka) | 60 мин |
| Лекција 4 | [Лице: очи, уста и умор](https://edgeai.tsp.edu.rs/lms/lice-i-umor) | 60 мин |
| Лекција 5 | [Слој преко камере](https://edgeai.tsp.edu.rs/lms/sloj-preko-kamere) | 75 мин |
| Лекција 6 | [LiDAR: свет из растојања](https://edgeai.tsp.edu.rs/lms/lidar-i-daljina) | 60 мин |
| Лекција 7 | [Од примера до пројекта](https://edgeai.tsp.edu.rs/lms/od-primera-do-projekta) | 45 мин |

## Брзи почетак

```bash
# сајт
cd web && npm install && npm run dev                 # http://localhost:5173

# један пројекат (пример: Усправно)
cd projekti/uspravno
python -m venv .venv && source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -e ".[dev]" && pytest

# примери за Raspberry Pi 5
cd lms/primeri && ./pokreni.sh                       # види lms/primeri/README.md
```

VS Code: **Run and Debug** има готове конфигурације за сајт и за Python пројекте.

## Структура репоа

| путања | шта је |
|---|---|
| [`web/`](web) | сајт (React + Vite + react-three-fiber): пројекти, упутства, Учионица, 3D насловна |
| [`projekti/`](projekti) | 12 ученичких пројеката (Python) |
| [`lms/primeri/`](lms/primeri) | примери за Raspberry Pi 5 уз лекције |
| [`docs/`](docs) | документација: [приватност](docs/privatnost.md), нацрти |
| [`deploy/`](deploy) | аутоматски деплој на Virtualmin (Node сервис + PM2 + `deploy.sh`) |
| `.github/workflows/` | CI: билд сајта и тестови пројеката |
| `.claude/skills/` | пројектни skill-ови за Claude Code |

## Деплој

`git push` у `main` → GitHub webhook → Node сервис (PM2) на серверу преведе и објави
сајт за ~1 минут (rollback ако build падне). Поставка, ротација тајне и решавање
проблема: [`deploy/README.md`](deploy/README.md).

## Приватност, безбедност, лиценце

- Подаци ученика (камера, глас): [`docs/privatnost.md`](docs/privatnost.md).
- Пријава безбедносних проблема: [`SECURITY.md`](SECURITY.md).
- Допринос: [`CONTRIBUTING.md`](CONTRIBUTING.md).
- Кôд: [MIT](LICENSE). Садржај сајта, упутства и лекције: [CC BY-SA 4.0](LICENSE-CONTENT).
- Материјал трећих страна и отворена питања лиценце: [`CREDITS.md`](CREDITS.md).

© 2026 Техничка школа Пирот
