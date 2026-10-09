# Дечје царство — игре за предшколце

![ниво: основно](https://img.shields.io/badge/%D0%BD%D0%B8%D0%B2%D0%BE-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE-2f6fed) ![хардвер: Camera Module 3](https://img.shields.io/badge/%D1%85%D0%B0%D1%80%D0%B4%D0%B2%D0%B5%D1%80-Camera_Module_3-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab)

Шест игара које се играју покретом шаке или лица испред камере, без читања. Покретач држи један мени и аутоматски гаси претходну игру да би ослободио камеру.

## Покретање

```bash
cd ~/primeri/igrice
python pokretac_igrice.py
```

## Игре

| игра | тастери |
|---|---|
| [Чаробни мехурићи](https://edgeai.tsp.edu.rs/lms/primeri/baloni) | `[r]` ресет · `[m]` звук · `[q]` назад |
| [Чаробни штапић](https://edgeai.tsp.edu.rs/lms/primeri/crtanje) | кажипрст црта · `[c]` бриши · `[t]` шаблон · `[q]` назад |
| [Ухвати звездице](https://edgeai.tsp.edu.rs/lms/primeri/korpica) | шака води корпицу · `[r]` ресет · `[m]` звук · `[q]` назад |
| [Нахрани животиње](https://edgeai.tsp.edu.rs/lms/primeri/nahrani) | штипање хвата храну · `[n]` следећа животиња · `[m]` звук · `[q]` назад |
| [Смешно огледало](https://edgeai.tsp.edu.rs/lms/primeri/ogledalo) | отвори уста за звездице · `[Space]`/`[n]` маска · `[m]` звук · `[q]` назад |
| [Спој исте сличице](https://edgeai.tsp.edu.rs/lms/primeri/sortiranje) | штипање хвата сличицу · `[r]` ресет нивоа · `[n]` следећи ниво |

## Како ради

- `pokretac_igrice.py` — мени. Тастери `[1]`–`[6]` покрећу игру, `[s]`/`[Space]` је заустављају, `[f]` пун екран, `[q]`/`[ESC]` излаз; може и мишем.
- Игре читају камеру и покрећу MediaPipe у посебним нитима (класа `FastVision…`), да цртање не чека на модел.
- У фолдеру су: `baloni/`, `crtanje/`, `korpica/`, `nahrani/`, `ogledalo/`. Шеста игра, `sortiranje`, налази се у засебном фолдеру `../sortiranje/`.

## Лекција и сајт

Прати лекцију: [Лекција 2: Руке, лице и покрет](https://edgeai.tsp.edu.rs/lms/ruke-i-pokret) · [Лекција 4: Лице: очи, уста и умор](https://edgeai.tsp.edu.rs/lms/lice-i-umor)
Страница примера на сајту: [Чаробни мехурићи](https://edgeai.tsp.edu.rs/lms/primeri/baloni)

Окружење и зависности: [`../README.md`](../README.md) · [`../requirements.txt`](../requirements.txt).
