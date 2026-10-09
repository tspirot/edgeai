# Пуцкетање — невидљивост

![ниво: средње](https://img.shields.io/badge/%D0%BD%D0%B8%D0%B2%D0%BE-%D1%81%D1%80%D0%B5%D0%B4%D1%9A%D0%B5-2f6fed) ![хардвер: Camera Module 3](https://img.shields.io/badge/%D1%85%D0%B0%D1%80%D0%B4%D0%B2%D0%B5%D1%80-Camera_Module_3-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab)

Пуцни прстима и нестани: особа се замењује снимком празне собе.

## Покретање

```bash
cd ~/primeri/pucketanje
python pucketanje.py
```

**Тастери:** [Space] невидљивост · [r] снимање позадине · [q] излаз

## Како ради

- На почетку се снима празна соба (`[r]` је снима поново) — током игре не помери камеру.
- Selfie Segmentation даје маску особе (вероватноћа > 0,55), која се проширује и замењује позадином помоћу `np.where`.
- Пуцањ је машина стања: `IDLE` → `READY` (палац и средњи прст спојени) → пуцањ (растојање > 0,48 дужине длана), са паузом 0,9 s. Алтернатива: `[Space]`.
- Тастери: `[c]` замена R/B, `[n]` NoIR баланс, `[r]` нова позадина.

## Лекција и сајт

Прати лекцију: [Лекција 5: Слој преко камере](https://edgeai.tsp.edu.rs/lms/sloj-preko-kamere)
Страница примера на сајту: [Пуцкетање — невидљивост](https://edgeai.tsp.edu.rs/lms/primeri/pucketanje)

Окружење и зависности: [`../README.md`](../README.md) · [`../requirements.txt`](../requirements.txt).
