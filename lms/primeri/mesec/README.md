# Месец у длану

![ниво: средње](https://img.shields.io/badge/%D0%BD%D0%B8%D0%B2%D0%BE-%D1%81%D1%80%D0%B5%D0%B4%D1%9A%D0%B5-2f6fed) ![хардвер: Camera Module 3](https://img.shields.io/badge/%D1%85%D0%B0%D1%80%D0%B4%D0%B2%D0%B5%D1%80-Camera_Module_3-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab)

Тродимензионални месец лебди изнад шаке, прати је и осветљава лице и собу.

## Покретање

```bash
cd ~/primeri/mesec
python mesec.py
```

**Тастери:** [m] тема · [+/−] величина · [q] излаз

## Како ради

- Положај месеца је просек палца, кажипрста и средишта длана; величина прати растојање прстију.
- Нови положај се меша са старим (65% старо, 35% ново), да месец не дрхти.
- Сјај настаје од неколико провидних слојева (`cv2.addWeighted`). Тастери: `[m]` тема, `[+]`/`[−]` величина.

## Лекција и сајт

Прати лекцију: [Лекција 5: Слој преко камере](https://edgeai.tsp.edu.rs/lms/sloj-preko-kamere)
Страница примера на сајту: [Месец у длану](https://edgeai.tsp.edu.rs/lms/primeri/mesec)

Окружење и зависности: [`../README.md`](../README.md) · [`../requirements.txt`](../requirements.txt).
