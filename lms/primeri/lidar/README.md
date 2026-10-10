# RPLIDAR C1 — 360° Laserski Radar & Skener (Raspberry Pi 5)

Test aplikacija i 360° radarski HUD za **Slamtec RPLIDAR C1** DTOF laserski skener povezan preko USB porta na Raspberry Pi 5.

![RPLIDAR C1 — 360° Laserski radar и skener](/slike/primeri/lidar.jpg)

---


## 🚀 Brzo pokretanje

### 1. Pokretanje grafičkog radara (TV / HDMI ekran):
```bash
source ~/primeri/env/bin/activate
cd ~/primeri/lidar
python lidar.py
```

### 2. Brzi test u konzoli / terminalu:
```bash
source ~/primeri/env/bin/activate
cd ~/primeri/lidar
python test_lidar.py
```

### 3. Matrix Konture Lica i Laserski Skener (TV ekran):
```bash
source ~/primeri/env/bin/activate
cd ~/primeri/lidar
python lidar_matrix_face.py
```
- Rekonstruiše 3D žičani hologram lica u zelenom Matrix stilu sa digitalnom kišom.
- Udaljenost sa LiDAR-a direktno upravlja veličinom i rotacijom lica.
- Kontrole: `[s]` Simulacija | `[c]` Teme | `[g]` Kiša ON/OFF | `[q]` Izlaz.

### 4. Sigurnosna Barijera (1m) i Alarm Upada (TV ekran):
```bash
source ~/primeri/env/bin/activate
cd ~/primeri/lidar
python lidar_alarm_barijera.py
```
- Prilikom pokretanja vrši inicijalno skeniranje (3.5 sekunde) i uči statički prostor.
- Sve postojeće objekte (nameštaj, zidove, noge stola unutar 1m) automatski IGNORIŠE!
- Filter malih pomeraja: Zahteva pomak od najmanje 20 cm od pozadine (eliminiše podrhtavanja i lepršanje).
- Filter malih objekata: Ignoriše objekte uže od 14 cm i ispod 4 tačke (eliminiše kablove, insekte, šum).
- Vremenski debouncer: Zahteva potvrdu u 3 uzastopna ciklusa pre aktivacije alarma.
- Kontrole: `[k]` Ponovna kalibracija (snimi prostor) | `[+]`/`[-]` Domet barijere | `[b]` Oblik zone | `[m]` Mute | `[r]` Reset | `[q]` Izlaz.

### 5. Preko objedinjenog pokretača (Jedan klik):
- Sa radne površine (Desktop): dvoklik na **`AI Projekti (Pokretač)`** i izaberite **LIDAR**.
- Iz terminala: `cd ~/primeri && ./pokreni.sh`

---

## 🎮 Kontrole tokom rada radara (`lidar.py`)

| Taster | Funkcija |
|---|---|
| `[+]` ili `[=]` | Povećaj domet prikaza (Zoom Out: 2m, 4m, 6m, 8m, 12m) |
| `[-]` ili `[_]` | Smanji domet prikaza (Zoom In) |
| `[s]` | Uključi / Isključi **SIMULACIJU** (demo soba dok senzor nije uključen) |
| `[c]` | Promeni temu boja (Sajber Neon, Vojni radar, Termalni Heatmap) |
| `[r]` | Ponovo pretraži USB portove i osveži vezu |
| `[m]` | Uključi / Isključi rotaciju motora |
| `[q]` ili `[ESC]` | Bezbedno zaustavljanje motora i izlaz |

---

## 🔌 Povezivanje i hardver

1. **RPLIDAR C1 USB Adapter:**
   - Povežite mali USB adapter koji dolazi uz C1 u bilo koji USB port na Raspberry Pi 5.
   - Uređaj će se automatski pojaviti kao `/dev/ttyUSB0` (ili `/dev/ttyACM0`).
2. **Brzina komunikacije (Baudrate):**
   - Fabrički standard za RPLIDAR C1 je **460800 baud** (za razliku od starijih A1 modela koji su radili na 115200). Aplikacija automatski prepoznaje i koristi 460800 baud.
3. **Dozvole (Permissions):**
   - Korisnik `pi` je već u `dialout` grupi. Ukoliko je potrebno ručno omogućiti pristup:
     ```bash
     sudo chmod 666 /dev/ttyUSB*
     ```
