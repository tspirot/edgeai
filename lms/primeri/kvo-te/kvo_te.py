#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
                    ПРОЈЕКАТ "КВО ТЕ" - ПИРОТСКИ АИ МОЗАК
                            Raspberry Pi 5 (kvo-te)
================================================================================
Опис:
  Интерактивна AI машина која одговара на питања на изворном пиротском
  дијалекту. Пружа савете о штедњи, храни (пеглана кобасица, качкаваљ),
  животу, времену, прича вицеве и говори кроз звучнике помоћу espeak-ng.

Контроле:
  - [Tastatura + ENTER]: Унеси било које питање
  - [1] - [6]: Брза питања по категоријама (Паре, Јело, Кво те мучи, Време...)
  - [r]: Објашњење случајне речи из пиротског речника
  - [m]: Укључи / искључи глас (Mute/Unmute TTS)
  - [f]: Преко целог екрана (Fullscreen)
  - [c]: Очисти екран
  - [ESC] или [q]: Излаз
================================================================================
"""

import os
import sys
import time
import argparse
import random

def _force_utf8() -> None:
    """Осигурава правилан UTF-8 испис на Windows конзоли без rušenja."""
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            try:
                reconfigure(encoding="utf-8")
            except Exception:
                pass

_force_utf8()

# Осигурај графички излаз на RPi Wayfire / Wayland / X11
if "DISPLAY" not in os.environ and sys.platform != "win32":
    os.environ["DISPLAY"] = ":0"
if "WAYLAND_DISPLAY" not in os.environ and sys.platform != "win32":
    os.environ["WAYLAND_DISPLAY"] = "wayland-0"

from pirotski_mozak import PirotskiMozak, PIROTSKI_RECNIK


# -----------------------------------------------------------------------------
# CLI REŽIM (Za rad direktno u SSH terminalu)
# -----------------------------------------------------------------------------
def pokreni_cli(mozak: PirotskiMozak, sa_zvukom: bool = True):
    print("\n" + "=" * 70)
    print("      К В О   Т Е   —   П И Р О Т С К И   А И   М О З А К")
    print("=" * 70)
    print("  'Кво те мучи, комшија? Питај шта оћеш, памет не наплаћујем!'")
    print("  Команде: 'izlaz' или 'q' за крај, 'vic' за виц, 'recnik' за речник.")
    print("=" * 70 + "\n")

    pozdrav = mozak.obradi_pitanje("здраво")
    print(f"🤖 ПИРОЋАНАЦ: {pozdrav}\n")
    if sa_zvukom:
        mozak.govori(pozdrav)

    while True:
        try:
            pitanje = input("👉 ТВОЈЕ ПИТАЊЕ: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nАјд са здравље, и чувај паре!")
            break

        if not pitanje:
            continue
        if pitanje.lower() in ["izlaz", "exit", "q", "крај"]:
            oprostaj = "Ајд са здравље, затварај врата и чувај паре под сламарицу!"
            print(f"\n🤖 ПИРОЋАНАЦ: {oprostaj}\n")
            if sa_zvukom:
                mozak.govori(oprostaj)
            break

        odgovor = mozak.obradi_pitanje(pitanje)
        print(f"\n🤖 ПИРОЋАНАЦ: {odgovor}\n")
        if sa_zvukom:
            mozak.govori(odgovor)


# -----------------------------------------------------------------------------
# PYGAME TV / HDMI EKRANSKI REŽIM
# -----------------------------------------------------------------------------
def pokreni_gui(fullscreen: bool = True, sa_zvukom: bool = True):
    import pygame

    pygame.init()
    pygame.font.init()

    info = pygame.display.Info()
    ekran_w = info.current_w if fullscreen else 1280
    ekran_h = info.current_h if fullscreen else 720

    flags = pygame.FULLSCREEN if fullscreen else 0
    prozor = pygame.display.set_mode((ekran_w, ekran_h), flags)
    pygame.display.set_caption("КВО ТЕ — Пиротски AI Мозак")

    clock = pygame.time.Clock()

    # Боје (Етно-Сајбер пиротска палета)
    C_BG = (18, 22, 28)           # Тамно сива позадина
    C_PANEL = (28, 35, 45)        # Панел боја
    C_BORDER = (220, 50, 40)      # Пиротско ћилим црвена
    C_GOLD = (235, 185, 55)       # Златна / жута боја качкаваља
    C_TEXT = (240, 240, 245)      # Бели текст
    C_SUBTEXT = (160, 175, 195)   # Светло плаво-сиви текст
    C_INPUT_BG = (12, 16, 22)     # Поље за унос
    C_GREEN = (60, 200, 110)      # Зелени статус

    # Фонтови (са пуном ћириличном подршком)
    def get_font(size):
        for fname in ["segoeui", "arial", "calibri", "dejavusans", "freesans", "liberationsans"]:
            try:
                f = pygame.font.SysFont(fname, size)
                if f:
                    return f
            except Exception:
                pass
        return pygame.font.Font(None, size)

    font_naslov = get_font(38)
    font_podnaslov = get_font(22)
    font_tekst = get_font(28)
    font_dugme = get_font(20)
    font_unos = get_font(26)

    mozak = PirotskiMozak()

    trenutno_pitanje = "Кво те мучи, комшија?"
    trenutni_odgovor = "Помоз' Бог! Улази, питај кво те мучи, ал' затварај врата да не бега топлота!"
    ispisani_odgovor = ""
    index_slova = 0
    vreme_poslednjeg_slova = time.time()

    unos_tekst = ""
    aktivan_unos = True
    glas_ukljucen = sa_zvukom
    je_fullscreen = fullscreen

    if glas_ukljucen:
        mozak.govori(trenutni_odgovor)

    # Категорије за брзе тастере
    kategorije = [
        ("[1] Паре", "паре и штедња"),
        ("[2] Јело", "пеглана кобасица и храна"),
        ("[3] Мука", "кво те мучи"),
        ("[4] Време", "време и нишавац"),
        ("[5] Љубав", "љубав и брак"),
        ("[6] Виц", "испричај ми пиротски виц"),
        ("[R] Речник", "речник"),
    ]

    running = True
    while running:
        dt = clock.tick(30)

        # Обрада догађаја
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE]:
                    running = False
                elif event.key == pygame.K_q and not aktivan_unos:
                    running = False
                elif event.key == pygame.K_f:
                    je_fullscreen = not je_fullscreen
                    flags = pygame.FULLSCREEN if je_fullscreen else 0
                    prozor = pygame.display.set_mode((ekran_w, ekran_h), flags)
                elif event.key == pygame.K_m:
                    glas_ukljucen = not glas_ukljucen
                elif event.key == pygame.K_c:
                    trenutno_pitanje = ""
                    trenutni_odgovor = "Питај кво те воља!"
                    ispisani_odgovor = trenutni_odgovor
                # Брзи тастери 1-6 (ако поље за унос није у фокусу за бројеве)
                elif event.key == pygame.K_1 and not unos_tekst:
                    trenutno_pitanje = "Како да уштедим паре?"
                    trenutni_odgovor = mozak.obradi_pitanje("паре")
                    ispisani_odgovor = ""
                    index_slova = 0
                    if glas_ukljucen: mozak.govori(trenutni_odgovor)
                elif event.key == pygame.K_2 and not unos_tekst:
                    trenutno_pitanje = "Шта се добро једе у Пирот?"
                    trenutni_odgovor = mozak.obradi_pitanje("храна")
                    ispisani_odgovor = ""
                    index_slova = 0
                    if glas_ukljucen: mozak.govori(trenutni_odgovor)
                elif event.key == pygame.K_3 and not unos_tekst:
                    trenutno_pitanje = "Кво те мучи?"
                    trenutni_odgovor = mozak.obradi_pitanje("кво те мучи")
                    ispisani_odgovor = ""
                    index_slova = 0
                    if glas_ukljucen: mozak.govori(trenutni_odgovor)
                elif event.key == pygame.K_4 and not unos_tekst:
                    trenutno_pitanje = "Какво је време данас?"
                    trenutni_odgovor = mozak.obradi_pitanje("време")
                    ispisani_odgovor = ""
                    index_slova = 0
                    if glas_ukljucen: mozak.govori(trenutni_odgovor)
                elif event.key == pygame.K_5 and not unos_tekst:
                    trenutno_pitanje = "Имаш ли неки љубавни савет?"
                    trenutni_odgovor = mozak.obradi_pitanje("љубав")
                    ispisani_odgovor = ""
                    index_slova = 0
                    if glas_ukljucen: mozak.govori(trenutni_odgovor)
                elif event.key == pygame.K_6 and not unos_tekst:
                    trenutno_pitanje = "Кажи ми један добар пиротски виц!"
                    trenutni_odgovor = mozak.obradi_pitanje("виц")
                    ispisani_odgovor = ""
                    index_slova = 0
                    if glas_ukljucen: mozak.govori(trenutni_odgovor)
                elif event.key == pygame.K_r and not unos_tekst:
                    rec = random.choice(list(PIROTSKI_RECNIK.keys()))
                    trenutno_pitanje = f"Шта значи реч '{rec}'?"
                    trenutni_odgovor = f"• '{rec.upper()}' значи: {PIROTSKI_RECNIK[rec]}"
                    ispisani_odgovor = ""
                    index_slova = 0
                    if glas_ukljucen: mozak.govori(trenutni_odgovor)
                # Унос са тастатуре
                elif event.key == pygame.K_RETURN:
                    if unos_tekst.strip():
                        trenutno_pitanje = unos_tekst.strip()
                        trenutni_odgovor = mozak.obradi_pitanje(trenutno_pitanje)
                        ispisani_odgovor = ""
                        index_slova = 0
                        unos_tekst = ""
                        if glas_ukljucen:
                            mozak.govori(trenutni_odgovor)
                elif event.key == pygame.K_BACKSPACE:
                    unos_tekst = unos_tekst[:-1]
                else:
                    if len(unos_tekst) < 70 and event.unicode and event.unicode.isprintable():
                        unos_tekst += event.unicode

        # Ефекат куцаће машине за одговор
        if index_slova < len(trenutni_odgovor):
            now = time.time()
            if now - vreme_poslednjeg_slova > 0.025:
                ispisani_odgovor += trenutni_odgovor[index_slova]
                index_slova += 1
                vreme_poslednjeg_slova = now

        # ИСЦРТАВАЊЕ
        prozor.fill(C_BG)

        # 1. Заглавље (Header)
        pygame.draw.rect(prozor, C_PANEL, (20, 20, ekran_w - 40, 90), border_radius=12)
        pygame.draw.rect(prozor, C_BORDER, (20, 20, ekran_w - 40, 90), width=2, border_radius=12)

        naslov_surf = font_naslov.render("КВО ТЕ  —  ПИРОТСКИ АИ МОЗАК", True, C_GOLD)
        prozor.blit(naslov_surf, (40, 32))

        podnaslov_surf = font_podnaslov.render("Локални оракул са Нишаве • Штедња, јело, мудрости и смех", True, C_SUBTEXT)
        prozor.blit(podnaslov_surf, (44, 75))

        # Ознаке статуса десно у заглављу
        status_glas = "ГЛАС: УКЉУЧЕН [m]" if glas_ukljucen else "ГЛАС: УТИШАН [m]"
        boja_glas = C_GREEN if glas_ukljucen else C_BORDER
        glas_surf = font_dugme.render(status_glas, True, boja_glas)
        prozor.blit(glas_surf, (ekran_w - 240, 42))

        pi_surf = font_dugme.render("100% ОФЛАЈН (Pi 5)", True, C_SUBTEXT)
        prozor.blit(pi_surf, (ekran_w - 240, 72))

        # 2. Леви визуелни аватар (Пироћанац са шубаром)
        avatar_w = 260
        avatar_h = 360
        avatar_x = 30
        avatar_y = 130
        pygame.draw.rect(prozor, C_PANEL, (avatar_x, avatar_y, avatar_w, avatar_h), border_radius=14)
        pygame.draw.rect(prozor, C_GOLD, (avatar_x, avatar_y, avatar_w, avatar_h), width=2, border_radius=14)

        # Лик: Цртамо симпатичног чичу са шубаром и брковима
        cx, cy = avatar_x + avatar_w // 2, avatar_y + 160
        # Шубара (црна/тамна са црвеним ћилим детаљем)
        pygame.draw.rect(prozor, (40, 35, 30), (cx - 75, cy - 110, 150, 70), border_radius=16)
        pygame.draw.rect(prozor, C_BORDER, (cx - 75, cy - 50, 150, 10))
        # Глава / лице
        pygame.draw.circle(prozor, (235, 195, 155), (cx, cy - 20), 55)
        # Очи
        pygame.draw.circle(prozor, (30, 30, 30), (cx - 20, cy - 30), 6)
        pygame.draw.circle(prozor, (30, 30, 30), (cx + 20, cy - 30), 6)
        # Нос
        pygame.draw.ellipse(prozor, (215, 160, 130), (cx - 8, cy - 25, 16, 22))
        # Велики бели пиротски бркови
        pygame.draw.ellipse(prozor, (240, 240, 240), (cx - 45, cy - 8, 90, 26))
        # Уста која се помало отварају ако текст још куца
        if index_slova < len(trenutni_odgovor) and int(time.time() * 8) % 2 == 0:
            pygame.draw.ellipse(prozor, (150, 40, 40), (cx - 14, cy + 10, 28, 14))
        else:
            pygame.draw.line(prozor, (100, 30, 30), (cx - 14, cy + 16), (cx + 14, cy + 16), 3)

        label_avatar = font_dugme.render("ЧИЧА ВИТОМИР", True, C_GOLD)
        prozor.blit(label_avatar, (cx - label_avatar.get_width() // 2, avatar_y + 280))
        label_lokacija = font_dugme.render("Тијабара, Пирот", True, C_SUBTEXT)
        prozor.blit(label_lokacija, (cx - label_lokacija.get_width() // 2, avatar_y + 310))

        # 3. Главни дијалошки панел (Десно)
        panel_x = avatar_x + avatar_w + 20
        panel_w = ekran_w - panel_x - 30
        panel_h = avatar_h

        pygame.draw.rect(prozor, C_PANEL, (panel_x, avatar_y, panel_w, panel_h), border_radius=14)
        pygame.draw.rect(prozor, (50, 65, 85), (panel_x, avatar_y, panel_w, panel_h), width=2, border_radius=14)

        # Приказ постављеног питања
        q_label = font_podnaslov.render("ПИТАЊЕ:", True, C_GOLD)
        prozor.blit(q_label, (panel_x + 25, avatar_y + 20))
        q_val = font_tekst.render(f"\"{trenutno_pitanje}\"", True, C_TEXT)
        prozor.blit(q_val, (panel_x + 25, avatar_y + 50))

        pygame.draw.line(prozor, (45, 55, 70), (panel_x + 20, avatar_y + 95), (panel_x + panel_w - 20, avatar_y + 95), 1)

        # Приказ одговора са преламањем редова (Word Wrap)
        ans_label = font_podnaslov.render("ОДГОВОР:", True, C_BORDER)
        prozor.blit(ans_label, (panel_x + 25, avatar_y + 110))

        # Преламање текста одговора
        max_sirina = panel_w - 50
        reci = ispisani_odgovor.split()
        linije = []
        trenutna_linija = ""
        for rec in reci:
            test_linija = f"{trenutna_linija} {rec}".strip()
            if font_tekst.size(test_linija)[0] < max_sirina:
                trenutna_linija = test_linija
            else:
                linije.append(trenutna_linija)
                trenutna_linija = rec
        if trenutna_linija:
            linije.append(trenutna_linija)

        red_y = avatar_y + 145
        for lin in linije[:6]:  # прикажи до 6 редова
            l_surf = font_tekst.render(lin, True, C_TEXT)
            prozor.blit(l_surf, (panel_x + 25, red_y))
            red_y += 36

        # 4. Трака са брзим категоријама
        kat_y = avatar_y + avatar_h + 20
        dx = 30
        for dugme_tekst, _ in kategorije:
            d_surf = font_dugme.render(dugme_tekst, True, C_TEXT)
            dw = d_surf.get_width() + 20
            pygame.draw.rect(prozor, C_PANEL, (dx, kat_y, dw, 36), border_radius=8)
            pygame.draw.rect(prozor, (70, 85, 110), (dx, kat_y, dw, 36), width=1, border_radius=8)
            prozor.blit(d_surf, (dx + 10, kat_y + 8))
            dx += dw + 12

        # 5. Поље за унос текста са тастатуре (Input box)
        input_y = kat_y + 55
        input_w = ekran_w - 60
        input_h = 56

        pygame.draw.rect(prozor, C_INPUT_BG, (30, input_y, input_w, input_h), border_radius=10)
        pygame.draw.rect(prozor, C_GOLD if aktivan_unos else (60, 70, 85), (30, input_y, input_w, input_h), width=2, border_radius=10)

        # Текст у пољу или placeholder
        if unos_tekst:
            prikaz_unosa = unos_tekst
            boja_unosa = C_TEXT
        else:
            prikaz_unosa = "Упиши питање овде па притисни [ENTER] (или кликни брзе тастере 1-6)..."
            boja_unosa = C_SUBTEXT

        u_surf = font_unos.render(prikaz_unosa, True, boja_unosa)
        prozor.blit(u_surf, (46, input_y + 14))

        # Трепћући курсор
        if aktivan_unos and unos_tekst and int(time.time() * 2) % 2 == 0:
            cursor_x = 46 + font_unos.size(unos_tekst)[0] + 4
            pygame.draw.line(prozor, C_GOLD, (cursor_x, input_y + 12), (cursor_x, input_y + 44), 2)

        # 6. Доња трака са упутствима
        info_tekst = "[ENTER] Постави питање  •  [1-6] Брзе теме  •  [R] Речник  •  [M] Глас  •  [F] Цео екран  •  [ESC/Q] Излаз"
        inf_surf = font_dugme.render(info_tekst, True, C_SUBTEXT)
        prozor.blit(inf_surf, (ekran_w // 2 - inf_surf.get_width() // 2, ekran_h - 32))

        pygame.display.flip()

    pygame.quit()


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="КВО ТЕ — Пиротски AI Мозак")
    parser.add_argument("--web", action="store_true", help="Покрени богати веб интерфејс (http://localhost:8080)")
    parser.add_argument("--cli", action="store_true", help="Покрени у терминали без графичког интерфејса")
    parser.add_argument("--windowed", action="store_true", help="Покрени у прозору уместо преко целог екрана")
    parser.add_argument("--fullscreen", action="store_true", help="Покрени преко целог екрана")
    parser.add_argument("--bez-zvuka", action="store_true", help="Искључи синтезу говора")
    args = parser.parse_args()

    if args.web:
        from web_kvo_te import pokreni_server
        pokreni_server(port=8080, otvori_browser=True)
        return

    mozak = PirotskiMozak()

    if args.cli:
        pokreni_cli(mozak, sa_zvukom=not args.bez_zvuka)
    else:
        # На Windows-у је згодније да крене као прозор ако није другачије наведено
        je_fullscreen = (sys.platform != "win32")
        if args.windowed:
            je_fullscreen = False
        if args.fullscreen:
            je_fullscreen = True

        try:
            pokreni_gui(fullscreen=je_fullscreen, sa_zvukom=not args.bez_zvuka)
        except Exception as e:
            print(f"Није могуће покренути графички интерфејс ({e}). Пребацујем на CLI режим...\n")
            pokreni_cli(mozak, sa_zvukom=not args.bez_zvuka)


if __name__ == "__main__":
    main()
