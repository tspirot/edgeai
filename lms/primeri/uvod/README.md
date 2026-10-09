# Увод: NumPy и OpenCV

![ниво: основно](https://img.shields.io/badge/%D0%BD%D0%B8%D0%B2%D0%BE-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE-2f6fed) ![хардвер: без камере (прве две)](https://img.shields.io/badge/%D1%85%D0%B0%D1%80%D0%B4%D0%B2%D0%B5%D1%80-%D0%B1%D0%B5%D0%B7_%D0%BA%D0%B0%D0%BC%D0%B5%D1%80%D0%B5_%28%D0%BF%D1%80%D0%B2%D0%B5_%D0%B4%D0%B2%D0%B5%29-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab)

Три мале скрипте које раде и на лаптопу — најпре низови, па слика, па камера.

## Покретање

```bash
cd ~/primeri/uvod
python numpy_kadar.py
python opencv_slika.py
python opencv_kamera.py
```

## Примери

| пример | покретање | тастери |
|---|---|---|
| [NumPy: кадар као низ](https://edgeai.tsp.edu.rs/lms/primeri/numpy-kadar) | `python numpy_kadar.py` | — |
| [OpenCV: једна слика](https://edgeai.tsp.edu.rs/lms/primeri/opencv-slika) | `python opencv_slika.py --snimi` | [q] или [ESC] излаз · --snimi уписује izlaz.png без прозора |
| [OpenCV: петља са камером](https://edgeai.tsp.edu.rs/lms/primeri/opencv-kamera) | `python opencv_kamera.py` | [q] или [ESC] излаз |

## Како ради

- `numpy_kadar.py` — прави кадар од нуле, чита му облик, сече област, прави маску и мења пикселе. Без камере и без екрана.
- `opencv_slika.py` — учитава `../logo.png`, црта, пребацује боје (BGR, сиво, HSV); `--snimi` уписује резултат у `izlaz.png`.
- `opencv_kamera.py` — најмања петља са камером: кадар, огледало, FPS, излаз на `[q]`.

## Лекција и сајт

Прати лекцију: [Увод 3: NumPy и низови](https://edgeai.tsp.edu.rs/lms/numpy-i-nizovi) · [Увод 4: OpenCV основе](https://edgeai.tsp.edu.rs/lms/opencv-osnove)
Страница примера на сајту: [NumPy: кадар као низ](https://edgeai.tsp.edu.rs/lms/primeri/numpy-kadar)

Окружење и зависности: [`../README.md`](../README.md) · [`../requirements.txt`](../requirements.txt).
