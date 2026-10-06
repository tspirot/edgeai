#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
       RPLIDAR C1 — BRZI KONZOLNI DIJAGNOSTIČKI TEST (CLI)
================================================================================
Testira USB vezu, očitava model, firmware, zdravlje i štampa udaljenosti
za 4 kardinalna pravca (Napred 0°, Desno 90°, Nazad 180°, Levo 270°).
"""

import os
import sys
import time
import serial
import serial.tools.list_ports

try:
    from rplidar import RPLidar
except ImportError:
    print("[GRESKA] 'rplidar-roboticia' nije instaliran!")
    print("Pokrenite: pip install rplidar-roboticia")
    sys.exit(1)

BAUDRATES_TO_TRY = [460800, 256000, 115200]


def pronadji_port():
    candidates = ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]
    for c in candidates:
        if os.path.exists(c):
            return c
    ports = serial.tools.list_ports.comports()
    for p in ports:
        desc = p.description.lower()
        if any(k in desc for k in ["cp210", "ch340", "ftdi", "silicon", "rplidar", "usb serial"]):
            return p.device
        if "ttyusb" in p.device.lower() or "ttyacm" in p.device.lower():
            return p.device
    return None


def main():
    print("=" * 65)
    print("     RPLIDAR C1 — KONZOLNI TEST I DIJAGNOSTIKA")
    print("=" * 65)

    port = pronadji_port()
    if not port:
        print("\n❌ NIJEDAN USB SERIJSKI PORT NIJE PRONAĐEN!")
        print("1. Povežite RPLIDAR C1 u bilo koji USB port na Raspberry Pi 5.")
        print("2. Proverite kabl i adapter.")
        print("3. U terminalu proverite komandom: ls -l /dev/ttyUSB*")
        return 1

    print(f"\n🔌 Detektovan port: {port}")

    lidar = None
    connected_baud = None

    for baud in BAUDRATES_TO_TRY:
        print(f"Pokušavam povezivanje na {baud} bps...")
        try:
            lidar = RPLidar(port, baudrate=baud, timeout=2)
            info = lidar.get_info()
            health = lidar.get_health()
            connected_baud = baud
            print(f"✅ USPEH na {baud} bps!")
            print("-" * 65)
            print(f"  Model senzora:     {info.get('model', 'RPLIDAR C1')}")
            print(f"  Firmware verzija:  {info.get('firmware', 'N/A')}")
            print(f"  Hardware verzija:  {info.get('hardware', 'N/A')}")
            print(f"  Serijski broj:     {info.get('serialnumber', 'N/A')}")
            print(f"  Status senzora:    {health[0] if isinstance(health, tuple) else health}")
            print("-" * 65)
            break
        except Exception as err:
            print(f"  Baud {baud} nije odgovorio ({err})")
            if lidar:
                try:
                    lidar.disconnect()
                except Exception:
                    pass
            lidar = None

    if not lidar:
        print("\n❌ Nije moguće uspostaviti komunikaciju sa senzorom.")
        print("Proverite dozvole: sudo chmod 666 " + port)
        return 1

    print("\nPokrećem motor skenera (Pritisnite Ctrl+C za prekid)...")
    try:
        lidar.start_motor()
        time.sleep(1.0)

        cardinal_dirs = {
            "NAPRED (0°)": 0,
            "DESNO  (90°)": 90,
            "NAZAD  (180°)": 180,
            "LEVO   (270°)": 270
        }

        readings = {}
        scan_count = 0

        for scan in lidar.iter_scans(max_buf_meas=800):
            scan_count += 1
            for qual, angle, dist_mm in scan:
                if dist_mm > 0:
                    deg = int(round(angle)) % 360
                    readings[deg] = dist_mm

            if scan_count % 5 == 0 and len(readings) > 50:
                print(f"\n--- SKEN #{scan_count} (Ukupno tačaka u 360°: {len(readings)}) ---")
                for name, target_deg in cardinal_dirs.items():
                    # Uzmi prosek ili najbliži ugao u opsegu +- 5 stepeni
                    near_dists = [readings[a] for a in range(target_deg - 5, target_deg + 6) if (a % 360) in readings]
                    if near_dists:
                        avg_cm = sum(near_dists) / len(near_dists) / 10.0
                        bar = "█" * int(min(avg_cm / 10.0, 30))
                        print(f"  {name:14s}: {avg_cm:6.1f} cm  {bar}")
                    else:
                        print(f"  {name:14s}: -- cm")

                if scan_count >= 50:
                    print("\n✅ Test je uspešno pročitao 50 krugova! Prekidam test.")
                    break

    except KeyboardInterrupt:
        print("\nPrekinuto od strane korisnika.")
    finally:
        print("Zaustavljam motor i gasim senzor...")
        try:
            lidar.stop()
            lidar.stop_motor()
            lidar.disconnect()
        except Exception:
            pass
        print("✅ Senzor je bezbedno zaustavljen.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
