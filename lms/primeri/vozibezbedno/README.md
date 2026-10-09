# Вози безбедно — праћење умора

![ниво: средње](https://img.shields.io/badge/%D0%BD%D0%B8%D0%B2%D0%BE-%D1%81%D1%80%D0%B5%D0%B4%D1%9A%D0%B5-2f6fed) ![хардвер: Camera Module 3](https://img.shields.io/badge/%D1%85%D0%B0%D1%80%D0%B4%D0%B2%D0%B5%D1%80-Camera_Module_3-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab)

Face Mesh прати очи, уста и нагиб главе и упозорава на умор.

## Покретање

```bash
cd ~/primeri/vozibezbedno
python vozibezbedno.py
```

## Како ради

- EAR (отвореност ока) испод 0,22 дуже од 1,3 s пали аларм за поспаност; MAR изнад 0,55 је зевање.
- PERCLOS је проценат последњих 150 кадрова са склопљеним оком; нагиб главе даје `cv2.solvePnP` на 6 тачака лица.
- **Ово је школски експеримент, не сигурносни уређај:** прагови су подешени за једну камеру и једно лице.

## Лекција и сајт

Прати лекцију: [Лекција 4: Лице: очи, уста и умор](https://edgeai.tsp.edu.rs/lms/lice-i-umor)
Страница примера на сајту: [Вози безбедно](https://edgeai.tsp.edu.rs/lms/primeri/vozibezbedno)

Окружење и зависности: [`../README.md`](../README.md) · [`../requirements.txt`](../requirements.txt).
