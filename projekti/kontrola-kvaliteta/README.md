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

## Лиценца

MIT (`LICENSE`).
