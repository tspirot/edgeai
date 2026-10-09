# Провера камере и препознавање руку

![ниво: основно](https://img.shields.io/badge/%D0%BD%D0%B8%D0%B2%D0%BE-%D0%BE%D1%81%D0%BD%D0%BE%D0%B2%D0%BD%D0%BE-2f6fed) ![хардвер: Camera Module 3](https://img.shields.io/badge/%D1%85%D0%B0%D1%80%D0%B4%D0%B2%D0%B5%D1%80-Camera_Module_3-c51a4a) ![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-3776ab)

Три мале скрипте: прва две проверавају да ли камера ради и у ком формату даје боје, трећа броји подигнуте прсте.

## Покретање

```bash
cd ~/primeri/test
python check_cam.py
python check_format.py
python proba.py
```

## Примери

| пример | покретање | тастери |
|---|---|---|
| [Провера камере](https://edgeai.tsp.edu.rs/lms/primeri/test-kamere) | `python check_cam.py` | — |
| [Препознавање руку](https://edgeai.tsp.edu.rs/lms/primeri/prepoznavanje-ruku) | `python proba.py` | [n] NoIR филтер · [+/−] засићење · [q] излаз |

## Како ради

- `check_cam.py` хвата један кадар преко Picamera2 и исписује његов облик и просек сваког канала.
- `check_format.py` прави два кадра (формати `BGR888` и `RGB888`) и исписује исти пиксел из оба — тако се види који је редослед канала.
- `proba.py` покреће MediaPipe Hands, броји подигнуте прсте и црта правоугаоник између палчева и кажипрста обе шаке. Тастери: `[n]` NoIR филтер, `[+]`/`[−]` засићење, `[q]` излаз.

## Лекција и сајт

Прати лекцију: [Лекција 1: Камера и слика](https://edgeai.tsp.edu.rs/lms/kamera-i-slika) · [Лекција 2: Руке, лице и покрет](https://edgeai.tsp.edu.rs/lms/ruke-i-pokret)
Страница примера на сајту: [Провера камере](https://edgeai.tsp.edu.rs/lms/primeri/test-kamere)

Окружење и зависности: [`../README.md`](../README.md) · [`../requirements.txt`](../requirements.txt).
