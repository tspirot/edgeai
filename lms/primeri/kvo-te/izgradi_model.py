#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
          ИЗГРАДЊА МОДЕЛА ПИРОТСКОГ ГОВОРА ИЗ РЕЧНИКА САНУ (PDF / TXT)
================================================================================
Аутор изворног речника: Драгољуб Златковић, 
"Друга допуна Речнику пиротског говора", 
Српски дијалектолошки зборник LXVII, САНУ 2020.

Ова скрипта:
  1. Извлачи текст из recnik.pdf (преко pdftotext или pypdf) ако recnik.txt не постоји.
  2. Филтрира заглавља, футере и нумерацију страница.
  3. Парсира одреднице, врсте речи, значења и аутентичне примере са терена.
  4. Гради двосмерни индекс:
     - Пиротски -> Српски (са значењима и примерима)
     - Српски -> Пиротски (обратни индекс појмова)
     - Корпус аутентичних реченица
  5. Снима готов модел у 'pirotski_model.json' у истом директоријуму.
================================================================================
"""

import os
import re
import sys
import json
import subprocess
from pathlib import Path


def ocisti_tekst(txt: str) -> str:
    """Уклања дијакритике и полугласнике ради лакше претраге."""
    t = txt.lower()
    t = t.replace("ь", "")
    t = t.replace("`", "").replace("´", "").replace("’", "").replace("'", "")
    t = re.sub(r'[\,\.\;\:\!\?\"\(\)\[\]]', '', t)
    return t.strip()


def izvuci_tekst_iz_pdf(pdf_path: Path, txt_path: Path) -> bool:
    """Извлачи текст из PDF-а помоћу pdftotext алата."""
    if txt_path.exists() and txt_path.stat().st_size > 10000:
        print(f"Постоји већ екстрахован '{txt_path.name}'.")
        return True

    print(f"Екстрахујем текст из '{pdf_path}'...")
    try:
        subprocess.run(["pdftotext", "-layout", str(pdf_path), str(txt_path)], check=True)
        print("pdftotext успешно извршен.")
        return True
    except Exception as e:
        print(f"pdftotext није успео ({e}), покушавам са Python библиотекама...")
        try:
            from pypdf import PdfReader
            reader = PdfReader(str(pdf_path))
            with open(txt_path, "w", encoding="utf-8") as out:
                for page in reader.pages:
                    out.write(page.extract_text() or "")
                    out.write("\n\x0c\n")
            return True
        except Exception as e2:
            print(f"Грешка при екстракцији: {e2}")
            return False


def parsuj_recnik(txt_path: Path) -> dict:
    """Парсује recnik.txt и прави структурирани речник."""
    print("Парсујем пиротски речник...")
    with open(txt_path, "r", encoding="utf-8", errors="ignore") as f:
        linije = f.readlines()

    # Пронађи почетак речника (Слово А, после упутства и скраћеница)
    start_idx = 0
    for idx, line in enumerate(linije):
        if "Друга допуна Речнику пиротског говора" in line or "ДРУГА ДОПУНА РЕЧНИКУ ПИРОТСКОГ ГОВОРА" in line:
            # Тражи слово А
            for j in range(idx, min(idx + 350, len(linije))):
                if re.match(r'^\s+а везн\.', linije[j]):
                    start_idx = j
                    break
            if start_idx > 0:
                break

    if start_idx == 0:
        # Fallback тражење прве одреднице
        for idx, line in enumerate(linije):
            if re.match(r'^\s+а везн\.', line):
                start_idx = idx
                break

    print(f"Речник почиње на линији {start_idx + 1}.")

    odrednice = []
    trenutna_odrednica = None
    bafer_teksta = []

    # Регуларни израз за заглавља и футере страница
    re_zaglavlje = re.compile(r'^\s*(Друга допуна Речнику пиротског говора|\d+\s+Драгољуб Златковић|Драгољуб Златковић\s+\d+|–\s*\d+\s*–|\x0c|\d+\s*$)')

    # Врсте речи које се појављују иза одреднице
    oznake_vrsta = (
        "везн.", "изр.", "м", "ж", "с", "прил.", "прид.", "свр.", "несвр.",
        "узв.", "реч.", "м/ж", "зб.", "арх.", "фиг.", "пеј.", "дем.", "аугм.",
        "н.п.", "грам.", "хиг."
    )

    def sacuvaj_odrednicu(odr_raw: str):
        if not odr_raw:
            return
        odr_raw = odr_raw.strip()
        # Тражи пример: иза црте '–'
        primeri = []
        znacenje = ""
        vrsta = ""
        rec = ""

        delovi_primer = re.split(r'\s+–\s+', odr_raw, maxsplit=1)
        glavni_deo = delovi_primer[0].strip()
        if len(delovi_primer) > 1:
            primer_tekst = delovi_primer[1].strip()
            # Може бити више примера одвојених тачком
            primeri.append(primer_tekst)

        # Раздвајање речи, врсте и значења
        # Обично: "абьр м добра вест." или "аљав, -а, -о неодговоран; неваспитан."
        # Тражимо прву ознаку врсте речи
        pronadjena_vrsta = None
        for oz in oznake_vrsta:
            match = re.search(r'\b' + re.escape(oz), glavni_deo)
            if match:
                if pronadjena_vrsta is None or match.start() < pronadjena_vrsta[0]:
                    pronadjena_vrsta = (match.start(), match.end(), oz)

        if pronadjena_vrsta:
            start_v, end_v, oz = pronadjena_vrsta
            rec = glavni_deo[:start_v].strip()
            vrsta = oz
            znacenje = glavni_deo[end_v:].strip()
        else:
            # Нема експлицитне ознаке, прва или прве две речи су одредница
            tokens = glavni_deo.split()
            if len(tokens) >= 2:
                rec = tokens[0]
                znacenje = " ".join(tokens[1:])
            else:
                rec = glavni_deo
                znacenje = ""

        rec = rec.rstrip(".,;")
        znacenje = znacenje.lstrip(".,;: ").rstrip(".,; ")

        if rec and (znacenje or primeri):
            rec_cista = ocisti_tekst(rec)
            odrednice.append({
                "rec": rec,
                "rec_cista": rec_cista,
                "vrsta": vrsta,
                "znacenje": znacenje,
                "primeri": primeri
            })

    # Пролазимо кроз линије речника
    for i in range(start_idx, len(linije)):
        l = linije[i].rstrip("\r\n")

        # Прескочи заглавља, футере и бројеве страница
        if re_zaglavlje.match(l) or not l.strip():
            continue

        # Прекид на крају зборника ако почне следећи рад
        if "Речи и изрази традиционалне исхране" in l or "Јакша Динић" in l:
            break

        # Нова одредница почиње са увлачењем (3-8 размака) и малим или великим словом
        # у речнику су све одреднице увучене са 5 размака
        je_nova_odrednica = bool(re.match(r'^\s{3,8}[а-шА-Шљњерџчћђѕь]', l))

        if je_nova_odrednica:
            if bafer_teksta:
                sacuvaj_odrednicu(" ".join(bafer_teksta))
                bafer_teksta = []
            bafer_teksta.append(l.strip())
        else:
            # Наставак претходне одреднице
            if bafer_teksta:
                bafer_teksta.append(l.strip())

    if bafer_teksta:
        sacuvaj_odrednicu(" ".join(bafer_teksta))

    print(f"Укупно парсирано одредница: {len(odrednice)}")

    # Изградња индекса
    indeks_pirotski = {}
    indeks_srpski = {}
    svi_primeri = []

    for idx, odr in enumerate(odrednice):
        cista = odr["rec_cista"]
        if cista not in indeks_pirotski:
            indeks_pirotski[cista] = []
        indeks_pirotski[cista].append(idx)

        # Индексирање српских речи из значења за претрагу
        zn_reci = re.findall(r'\b[а-шА-Шa-zA-Z]{3,}\b', odr["znacenje"].lower())
        for zr in zn_reci:
            if zr not in indeks_srpski:
                indeks_srpski[zr] = []
            if idx not in indeks_srpski[zr]:
                indeks_srpski[zr].append(idx)

        # Прикупљање примера за корпус
        for p in odr["primeri"]:
            svi_primeri.append({
                "rec": odr["rec"],
                "tekst": p
            })

    model = {
        "meta": {
            "naslov": "Друга допуна Речнику пиротског говора",
            "autor": "Драгољуб Златковић",
            "izvor": "Српски дијалектолошки зборник LXVII, САНУ 2020.",
            "broj_odrednica": len(odrednice),
            "broj_primera": len(svi_primeri)
        },
        "odrednice": odrednice,
        "indeks_pirotski": indeks_pirotski,
        "indeks_srpski": indeks_srpski,
        "svi_primeri": svi_primeri
    }

    return model


def sacuvaj_model(model: dict, output_path: Path):
    """Снима генерисани модел у JSON фајл."""
    print(f"Снимам модел у '{output_path}'...")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(model, f, ensure_ascii=False, indent=2)
    velicina_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"Модел успешно снимљен! Величина: {velicina_mb:.2f} MB")


def main():
    root = Path(__file__).resolve().parent
    pdf_path = root / "recnik.pdf"
    txt_path = root / "recnik.txt"
    model_path = root / "pirotski_model.json"

    if not pdf_path.exists() and not txt_path.exists():
        print(f"Грешка: Не постоји ни {pdf_path} ни {txt_path}!")
        sys.exit(1)

    if not txt_path.exists():
        uspeh = izvuci_tekst_iz_pdf(pdf_path, txt_path)
        if not uspeh:
            sys.exit(1)

    model = parsuj_recnik(txt_path)
    sacuvaj_model(model, model_path)
    print("Завршено!")


if __name__ == "__main__":
    main()
