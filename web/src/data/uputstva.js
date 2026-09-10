/* Упутства и радне листе за радионице Edge AI. */

export const uputstva = [
  {
    slug: 'raspberry-pi-priprema',
    naziv: 'Припрема Raspberry Pi 5',
    kratko: 'Од празне microSD картице до система спремног за рад — ОС, хлађење, напајање, мрежа.',
    nivo: 'основно',
    vreme: '40 мин',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Свака радна станица креће од истог корака. Радимо на Raspberry Pi OS (64-bit), верзија „Bookworm“.' },
      { type: 'h', text: 'Шта треба' },
      { type: 'specs', items: ['Raspberry Pi 5 (8 GB)', 'microSD 64 GB', 'напајање 27 W / 5 A', 'активни хладњак', 'читач картица'] },
      { type: 'h', text: 'Кораци' },
      {
        type: 'steps',
        items: [
          'На рачунару инсталирај Raspberry Pi Imager и убаци microSD картицу.',
          'Изабери OS: Raspberry Pi OS (64-bit). Уређај: Raspberry Pi 5.',
          'У подешавањима (иконица зупчаника) укуцај име уређаја, корисника, лозинку, Wi-Fi и укључи SSH.',
          'Упиши картицу, стави је у Pi, прикључи активни хладњак и напајање.',
          'Сачекај прво подизање, па се повежи: ssh korisnik@ime-uredjaja.local',
        ],
      },
      { type: 'code', lang: 'bash', code: 'sudo apt update && sudo apt full-upgrade -y\nsudo reboot' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Основна радна станица',
        caption:
          'Овако изгледа Pi 5 пре него што му се дода било шта пројектно. Свака станица у лабораторији креће одавде.',
        data: {
          ploca: 'Raspberry Pi 5 (8 GB)',
          veze: [
            { port: 'USB-C', ikona: '🔌', naziv: 'Напајање 27 W / 5 A', detalj: 'слабије даје насумичне падове' },
            { port: 'GPIO', ikona: '🌀', naziv: 'Активни хладњак', detalj: 'без њега процесор успорава' },
            { port: 'microSD', ikona: '💾', naziv: 'Картица 64 GB', detalj: 'Raspberry Pi OS 64-bit' },
            { port: 'micro-HDMI', ikona: '🖥️', naziv: 'Монитор', detalj: 'или само SSH преко мреже' },
          ],
        },
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Напајање и хлађење нису опциони',
        text: 'Pi 5 под оптерећењем (инференца) вуче струју и греје се. Слабо напајање даје насумичне падове; без хладњака процесор успорава.',
      },
      { type: 'h', text: 'Провера' },
      { type: 'code', lang: 'bash', code: 'vcgencmd measure_temp\nvcgencmd get_throttled   # 0x0 значи да нема успоравања' },
    ],
  },

  {
    slug: 'ai-hat-hailo',
    naziv: 'AI HAT+ (Hailo-8L)',
    kratko: 'Монтажа акцелератора од 13 TOPS, инсталација софтвера и прва детекција објеката.',
    nivo: 'средње',
    vreme: '50 мин',
    sadrzaj: [
      { type: 'p', lead: true, text: 'AI HAT+ носи Hailo-8L чип за инференцу неуронских мрежа са сликом. Користе га „Паметна зебра“ и „Контрола квалитета“.' },
      { type: 'h', text: 'Монтажа' },
      {
        type: 'steps',
        items: [
          'Искључи напајање. Постави дистанце и повежи HAT преко PCIe FPC каблa.',
          'Причврсти HAT на GPIO и завртњима на дистанце.',
          'Укључи Pi и провери да ли систем види уређај на PCIe магистрали.',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Где шта иде',
        caption:
          'Најчешћа грешка при монтажи: FPC кабл се тражи на GPIO пиновима. Подаци иду искључиво преко PCIe прикључка — GPIO носи само механику и напајање додатака.',
        data: {
          ploca: 'Raspberry Pi 5',
          veze: [
            { port: 'PCIe', ikona: '⚡', naziv: 'AI HAT+ (Hailo-8L)', detalj: 'FPC кабл — овуда иду подаци' },
            { port: 'GPIO', ikona: '🔩', naziv: 'Дистанце и завртњи', detalj: 'механичко причвршћење' },
            { port: 'CSI', ikona: '📷', naziv: 'Камера', detalj: 'за проверу детекције' },
            { port: 'USB-C', ikona: '🔌', naziv: 'Напајање 27 W', detalj: 'плоча и HAT заједно' },
          ],
        },
      },
      { type: 'h', text: 'Софтвер' },
      { type: 'code', lang: 'bash', code: 'sudo apt update\nsudo apt install -y hailo-all\nsudo reboot' },
      { type: 'code', lang: 'bash', code: 'hailortcli fw-control identify   # треба да испише Hailo-8L\nrpicam-hello -t 5000              # провера камере' },
      { type: 'h', text: 'Прва детекција' },
      {
        type: 'p',
        text: 'У пакету rpicam-apps и hailo примера долази готова YOLOv8 пост-обрада. Покрени демо са камером и види оквире у реалном времену.',
      },
      { type: 'code', lang: 'bash', code: 'rpicam-hello -t 0 --post-process-file /usr/share/rpi-camera-assets/hailo_yolov8_inference.json' },
      {
        type: 'callout',
        tone: 'info',
        title: 'Радна листа за ученике',
        text: 'Задатак: измерити број кадрова у секунди са и без акцелератора, на истом моделу. Записати разлику и објаснити је.',
      },
    ],
  },

  {
    slug: 'ai-camera-imx500',
    naziv: 'Raspberry Pi AI Camera (IMX500)',
    kratko: 'Камера код које мрежа ради на самом сензору — поставка и учитавање модела.',
    nivo: 'средње',
    vreme: '45 мин',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Код IMX500 сензора инференца се дешава на чипу камере. Главни процесор добија већ готове резултате, па троши мало струје. Користе је „Чувар Старе планине“ и „Знаковна азбука“.' },
      { type: 'h', text: 'Поставка' },
      { type: 'code', lang: 'bash', code: 'sudo apt update\nsudo apt install -y imx500-all\nsudo reboot' },
      { type: 'code', lang: 'bash', code: 'rpicam-hello -t 10s --post-process-file /usr/share/rpi-camera-assets/imx500_mobilenet_ssd.json --viewfinder-width 1920 --viewfinder-height 1080' },
      {
        type: 'shema',
        kind: 'tok',
        naslov: 'Зашто је ово другачије',
        caption:
          'Код обичне камере кадар путује до процесора па се тек тамо обрађује. Код IMX500 мрежа ради на самом сензору, а процесор добија готов резултат — отуда потрошња од непуна 2 W.',
        pipeline: [
          { icon: '📷', title: 'IMX500 сензор', detail: 'кадар настаје на чипу' },
          { icon: '🧠', title: 'Мрежа на сензору', detail: 'инференца пре излаза из камере' },
          { icon: '📨', title: 'Само резултат', detail: 'ознака и оквир, не цела слика' },
          { icon: '😴', title: 'Pi већином спава', detail: 'буди се тек на налаз' },
        ],
      },
      { type: 'h', text: 'Свој модел' },
      {
        type: 'steps',
        items: [
          'Истренирај модел (нпр. класификатор врста) у уобичајеном алату.',
          'Конвертуј га Hailo/IMX500 алатом за паковање у формат сензора (.rpk).',
          'Укажи на .rpk фајл у post-process JSON-у и покрени.',
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Ограничења сензора',
        text: 'На сензор стаје мали модел. Пројектуј мрежу тако да улази у меморију IMX500 — то је део задатка, не препрека.',
      },
    ],
  },

  {
    slug: 'kuciste-laser-3d',
    naziv: 'Кућиште: ласер и 3D штампа',
    kratko: 'Израда кућишта за станице у школском Makers Lab-у — плексиглас на CO2 ласеру и носачи на 3D штампачу.',
    nivo: 'основно',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кућишта се не купују — праве се. То је садржај активности „набавка опреме и припрема лабораторије“ и прилика да ученици уђу у CAD и CAM.' },
      { type: 'h', text: 'Плексиглас (CO2 ласер)' },
      {
        type: 'steps',
        items: [
          'Нацртај странице кућишта у векторском алату (mm, 1:1).',
          'Додај „prst“ спојеве на ивицама и отворе за портове (USB, HDMI, камера, вентилација).',
          'Извези као SVG/DXF, постави брзину и снагу према дебљини плексигласа, исеци.',
          'Састави „на суво“, па залепи или споји завртњима M3.',
        ],
      },
      {
        type: 'shema',
        kind: 'kuciste',
        naslov: 'Страница кућишта — принцип',
        caption:
          'Дубина зупца мора да буде тачно једнака дебљини плексигласа. Ако је мања, спој не належе; ако је већа, зубац вири преко ивице.',
        data: {
          sirina: 'цртај у милиметрима, размера 1:1 — ласер реже онолико колико пише',
          otvori: [
            { naziv: 'USB', x: 10, y: 60, w: 22, h: 12 },
            { naziv: 'HDMI', x: 40, y: 60, w: 26, h: 11 },
            { naziv: 'камера', x: 76, y: 18, w: 16, h: 17 },
          ],
        },
      },
      { type: 'h', text: '3D штампа' },
      {
        type: 'ul',
        items: [
          'Носачи за Pi и HAT, држач камере са зглобом, поклопац за вентилатор.',
          'PLA је довољан за унутрашњу употребу; PETG за спољашње уређаје (фотозамка).',
          'Испуна 15–20%, 3 периметра, без подршки где год може.',
        ],
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Безбедност на ласеру',
        text: 'Никад PVC — при резу ослобађа хлор. Само материјали са познатим саставом, уз одсис и надзор наставника.',
      },
    ],
  },

  {
    slug: 'titlovi-uzivo-instalacija',
    naziv: 'Титлови уживо — инсталација',
    kratko: 'Постављање и покретање система за титловање на Raspberry Pi 5.',
    nivo: 'средње',
    vreme: '35 мин',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/titlovi-uzivo. Систем ради офлајн након што се модел преузме једном.' },
      { type: 'h', text: 'Инсталација' },
      { type: 'code', lang: 'bash', code: 'git clone https://github.com/tspirot/edgeai.git\ncd edgeai/projekti/titlovi-uzivo\npython3 -m venv .venv && source .venv/bin/activate\npip install -e .' },
      { type: 'h', text: 'Преузимање модела (једном, уз интернет)' },
      { type: 'code', lang: 'bash', code: 'titlovi download-model --backend faster-whisper --model base' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шта мора да буде прикључено',
        caption:
          'Мрежни кабл треба само за корак преузимања модела. Кад једном прође, извуци га — систем ради потпуно офлајн.',
        data: {
          ploca: 'Raspberry Pi 5 (8 GB)',
          veze: [
            { port: 'USB', ikona: '🎙️', naziv: 'USB микрофон', detalj: 'провери индекс: titlovi devices' },
            { port: 'HDMI', ikona: '🖥️', naziv: 'Пројектор', detalj: 'titlovi run — цео екран' },
            { port: 'LAN', ikona: '🌐', naziv: 'Мрежа', detalj: 'само за прво преузимање модела' },
          ],
        },
      },
      { type: 'h', text: 'Провера аудио улаза' },
      { type: 'code', lang: 'bash', code: 'titlovi devices' },
      { type: 'h', text: 'Покретање' },
      { type: 'code', lang: 'bash', code: '# титлови преко целог екрана (HDMI)\ntitlovi run\n\n# приказ у прегледачу на локалној мрежи\ntitlovi run --display web\n\n# проба без микрофона и без модела\ntitlovi run --backend dummy --console' },
      {
        type: 'callout',
        tone: 'info',
        title: 'Ћирилица или латиница',
        text: 'Подразумевано је ћирилица. Промени са titlovi run --script latin или у config.yaml.',
      },
    ],
  },

  {
    slug: 'uspravno-postavka',
    naziv: 'Усправно: постављање и калибрација',
    kratko: 'Камера са стране, MediaPipe Pose на Pi 5, лична калибрација, прагови и подсетник, приватност.',
    nivo: 'средње',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/uspravno. Циљ радионице: од камере до уређаја који прати држање ученика за столом и благо подсећа на исправљање — а притом ништа не снима и ништа не тврди о здрављу.' },
      { type: 'callout', tone: 'alert', title: 'Ово није медицински уређај', text: 'Систем мери навику држања и подсећа. Не поставља дијагнозу скалиозе ни кифозе. Упорна одступања → школски лекар. Тако мора да пише и на плочи изнад станице.' },
      { type: 'h', text: 'Прво симулација' },
      { type: 'code', lang: 'bash', code: 'cd edgeai/projekti/uspravno\npython3 -m venv .venv && source .venv/bin/activate\npip install -e ".[dev]"\npytest                    # 29 тестова: углови, монитор, скрининг\ndrzanje sim               # цео ланац без камере и модела' },
      { type: 'h', text: 'Камера и модел' },
      { type: 'code', lang: 'bash', code: 'sudo apt install -y python3-picamera2\npip install -e ".[kamera,poza]"    # OpenCV + MediaPipe Pose\ndrzanje devices                     # који је индекс камере' },
      {
        type: 'steps',
        items: [
          'Камеру постави са стране ученика, у висини рамена, 60–100 cm од столице.',
          'Треба да види уво, раме и кук у профилу — не одозго, не искоса.',
          '3D штампан држач да угао остане исти од часа до часа.',
          'Провери да ли се у кадру виде уво, раме и кук — то су три тачке из којих се рачунају углови.',
          'У config.yaml: pose.side (left/right, која страна тела гледа камеру) или остави auto.',
        ],
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Где стоји камера',
        caption:
          'Из профила се углови врата и трупа виде као прави углови. Постављена спреда или одозго, камера мери пројекцију угла — број који се мења кад се ученик само окрене.',
        data: {
          kamera: { naziv: 'Камера са стране', vfov: 52, visina: 'висина рамена' },
          zone: [{ naziv: 'Мерни кадар — уво, раме, кук', od: 26, do: 76 }],
          objekti: [
            { ikona: '🧍', naziv: 'Ученик у профилу', x: 50, y: 48 },
            { ikona: '🪑', naziv: 'Столица', x: 74, y: 60 },
            { ikona: '📏', naziv: '60–100 cm', x: 26, y: 30 },
          ],
          tlo: 'Радно место — поглед одозго',
        },
      },
      { type: 'h', text: 'Лична калибрација' },
      { type: 'code', lang: 'bash', code: 'drzanje calibrate        # ученик седи усправно и мирно ~5 s' },
      { type: 'p', text: 'Референца (два угла) се чува у data/referenca.json. Систем даље прати одступање од ње, не од просека — зато ради и за виши и за нижи раст.' },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Прагови се подешавају уживо',
        text: 'Ако подсетник пали пречесто, повећај posture.neck_threshold_deg / trunk_threshold_deg или alert_after_s. Ако не реагује на очиту погрбљеност, смањи их. clear_margin_deg спречава треперење око прага.',
      },
      { type: 'h', text: 'Рад и извештај' },
      { type: 'code', lang: 'bash', code: 'drzanje run --seconds 2700    # један школски час\ndrzanje report                # сажетак свих сесија\ndrzanje report --screening    # асиметрија кроз недеље (ако је режим укључен)' },
      { type: 'h', text: 'Приватност — провери' },
      {
        type: 'ul',
        items: [
          'У коду не постоји ниједан позив који снима слику на диск — само CSV са бројевима.',
          'Отвори data/drzanje.csv: датум, трајање, минути погрбљености, епизоде. Ниједно име, ниједна слика.',
          'На Demo Day-у то показати публици — то је пола поенте пројекта.',
        ],
      },
      { type: 'h', text: 'Провера — како знам да ради' },
      {
        type: 'ul',
        items: [
          'drzanje sim: у испису се смењују „ок“ и „ЛОШЕ“, епизода се изброји, стигне 🔔 подсетник.',
          'На камери: калибриши се усправно, па се погрби — после неколико секунди угао Δ прелази праг, после дужег времена стигне подсетник.',
          'Врати се у усправно — стање се очисти тек кад јасно пређеш испод прага (хистереза).',
        ],
      },
    ],
  },

  {
    slug: 'hodnik-u-glavi-slam',
    naziv: 'RPLIDAR SLAM: мапирање и навигација',
    kratko: 'Монтажа и оријентација RPLIDAR-а, калибрација „напред“, спор снимак мапе, читање мапе, планирање пута.',
    nivo: 'напредно',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/hodnik-u-glavi. Циљ радионице: направити мапу ходника једним ласерским сензором и пустити возило да само оде до тачке на мапи. Прво све у симулацији, па на правом RPLIDAR-у.' },
      { type: 'h', text: 'Прво симулација' },
      { type: 'code', lang: 'bash', code: 'cd edgeai/projekti/hodnik-u-glavi\npython3 -m venv .venv && source .venv/bin/activate\npip install -e ".[dev]"\npytest                                  # 30 тестова: ICP, grid, A*, pure pursuit\nmapa sim --goal 2.0 1.0 --out out/sim.png   # мапа + вожња до тачке' },
      { type: 'p', text: 'Отвори out/sim.png: бело = слободно, црно = зид, сиво = непознато, црвена тачка = процењен положај возила. „Грешка SLAM-а“ у испису је разлика процене и стварног положаја — треба да буде испод ~0.15 m.' },
      { type: 'h', text: 'RPLIDAR на возило' },
      {
        type: 'steps',
        items: [
          'Монтирај RPLIDAR на равну плочу изнад возила, што ближе центру ротације, да га делови возила не заклањају.',
          'Запамти у ком смеру гледа конектор мотора лидара — то је његова 0° тачка.',
          'Повежи USB. `mapa devices` → нађи /dev/ttyUSB* и упиши у config.yaml (lidar.port).',
          'sudo usermod -aG dialout $USER, па релогин (приступ порту без sudo).',
        ],
      },
      { type: 'h', text: 'Калибрација „напред“' },
      { type: 'p', text: 'SLAM претпоставља да лидарска 0° гледа право напред. Ако је сензор монтиран заокренуто, стави угао у lidar.forward_offset_deg (нпр. 90 или 180). Провера: стани возилом ка зиду на 1 m и мапирај 5 s — зид на мапи мора да буде тачно испред возила.' },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Провера оријентације',
        caption:
          'Постави возило управно на зид, на метар растојања, и мапирај пет секунди. Ако се зид на мапи појави са стране уместо испред — 0° лидара није поравнат са „напред“ и треба подесити forward_offset_deg.',
        data: {
          kamera: { naziv: 'RPLIDAR 0° — „напред“', vfov: 44, visina: '360°' },
          zone: [{ naziv: 'Очекивано: зид право испред', od: 56, do: 80 }],
          objekti: [
            { ikona: '🧱', naziv: 'Зид на 1 m', x: 50, y: 68 },
            { ikona: '🚗', naziv: 'Возило', x: 50, y: 12 },
          ],
          tlo: 'Провера пре мапирања — поглед одозго',
        },
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Спор сензор — спора вожња',
        text: 'RPLIDAR A1 се врти 5–6 пута у секунди. На брзини се скен „размаже“ и ICP склизне. Прво мапирај гурањем руком, полако; аутономну вожњу држи на најнижем гасу.',
      },
      { type: 'h', text: 'Снимак мапе' },
      { type: 'code', lang: 'bash', code: 'mapa map --seconds 90 --out out/skola.npz   # гурај возило споро кроз ходник\nmapa show out/skola.npz                       # погледај мапу\nmapa plan out/skola.npz --start 0 0 --goal 4 -1   # испланирај пут по готовој мапи' },
      { type: 'p', text: 'Ако мапа „бежи“ (зидови се дуплирају под углом), возио си пребрзо или је ходник предугачак без карактеристичних места — скрати деоницу.' },
      { type: 'h', text: 'Аутономна вожња' },
      { type: 'code', lang: 'bash', code: 'mapa navigate --goal 3 -1        # SLAM уживо + вожња до тачке (у оквиру старта)\nmapa navigate --goal 3 -1 -v     # детаљан испис: fitness ICP-а, дужина плана' },
      { type: 'p', text: 'Циљ је у метрима у односу на место где је возило кренуло (x напред, y лево).' },
      { type: 'h', text: 'Провера — како знам да ради' },
      {
        type: 'ul',
        items: [
          'mapa sim: „СТИГАО“ и грешка SLAM-а испод 0.15 m.',
          'mapa show: облик мапе се поклапа са тлоцртом просторије.',
          'На возилу: стани испред зида и мапирај — зид је право испред тачке возила (иначе подеси forward_offset_deg).',
          'mapa navigate: возило крене ка циљу и обиђе препреку коју ставиш на пут.',
        ],
      },
    ],
  },

  {
    slug: 'djak-za-volanom-postavka',
    naziv: 'PiRacer + RPLIDAR: постављање аутомобила',
    kratko: 'Склапање шасије, PCA9685 серво и ESC, камера напред, RPLIDAR на USB, калибрација волана и гаса, први круг.',
    nivo: 'напредно',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/djak-za-volanom. Циљ радионице: од кутије PiRacer-а до аута који одрађује круг у симулацији, па први спори круг на стази — са тврдим лимитом гаса и лидаром као кочницом.' },
      { type: 'h', text: 'Шта треба' },
      { type: 'specs', items: ['Waveshare PiRacer AI Kit', 'Raspberry Pi 4 (4 GB) + хладњак', 'камера (Camera Module 3 или USB, широки угао)', 'Slamtec RPLIDAR A1 + USB адаптер', '2× 18650 напуњене', 'Bluetooth гејмпад'] },
      { type: 'h', text: 'Склапање и напајање' },
      {
        type: 'steps',
        items: [
          'Састави шасију по Waveshare упутству: серво у предњи мост, ESC на мотор, PCA9685 на серво и ESC.',
          'Pi на носач, камеру напред са благим нагибом наниже (да види стазу 30–150 cm испред аута).',
          'RPLIDAR на равну површину изнад аута, конектор напред; повежи га USB каблом на Pi.',
          'Батерије за погон одвојено од напајања Pi-ја (power bank) — пад напона при трзају мотора руши Pi.',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања аутомобила',
        caption:
          'Две одвојене гране напајања нису препорука него услов: када мотор тргне, напон падне, и Pi се ресетује ако виси на истом пакету.',
        data: {
          ploca: 'Raspberry Pi 4 (4 GB)',
          veze: [
            { port: 'CSI / USB', ikona: '📷', naziv: 'Камера напред', detalj: 'нагиб наниже, 30–150 cm' },
            { port: 'USB', ikona: '🌀', naziv: 'RPLIDAR A1', detalj: 'конектор окренут напред' },
            { port: 'I²C', ikona: '🎛️', naziv: 'PCA9685', detalj: 'серво волана + ESC гаса' },
            { port: 'BT', ikona: '🎮', naziv: 'Гејмпад', detalj: 'ручна вожња при снимању' },
            { port: 'USB-C', ikona: '🔋', naziv: 'Power bank за Pi', detalj: 'ОДВОЈЕНО од 2× 18650' },
          ],
        },
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Точкови у ваздуху при првом тесту',
        text: 'Пре сваког volan drive и volan check, подигни ауто на кутију. ESC може да тргне пуном снагом ако је калибрација погрешна.',
      },
      { type: 'h', text: 'Софтвер' },
      { type: 'code', lang: 'bash', code: 'sudo apt install -y python3-venv pigpio\ngit clone https://github.com/tspirot/edgeai.git\ncd edgeai/projekti/djak-za-volanom\npython3 -m venv .venv && source .venv/bin/activate\npip install -e ".[kamera,lidar,pwm,gamepad]"' },
      { type: 'h', text: 'RPLIDAR — провера порта' },
      { type: 'code', lang: 'bash', code: 'volan devices                 # излистај /dev/ttyUSB*\nsudo usermod -aG dialout $USER  # једном, па релогин — приступ порту без sudo\nvolan check                    # камера + лидар + серво тест' },
      { type: 'p', text: 'Ако лидар није на /dev/ttyUSB0, упиши тачан порт у config.yaml (lidar.port).' },
      { type: 'h', text: 'Калибрација волана и гаса' },
      {
        type: 'steps',
        items: [
          'volan check врти серво лево → центар → десно. Ако центар није прав, подеси drive.steer_trim (−1..1).',
          'Ако ауто скреће супротно од очекиваног, стави drive.invert_steer: true.',
          'ESC: држи throttle_stop_us тако да мотор мирује; повећавај throttle_full_us опрезно.',
          'Постави drive.max_throttle на 0.35 за почетак — то је тврди лимит, не мења га модел.',
        ],
      },
      { type: 'h', text: 'Први круг' },
      { type: 'code', lang: 'bash', code: 'volan sim                     # цео ланац без хардвера — провера логике\nvolan drive --model heuristic # прати светлу траку, без снимања\n# тек кад ово ради поуздано: volan record → volan train → volan drive' },
      { type: 'h', text: 'Провера — како знам да ради' },
      {
        type: 'ul',
        items: [
          'volan sim: „Кочница активна у N/100 циклуса“ — препрека на пола симулације зауставља ауто.',
          'volan check: најближа тачка испред у mm се мења кад руком приђеш лидару.',
          'volan drive --model heuristic: ауто прати светлију траку и стаје кад му станеш испред.',
          'Искључиш RPLIDAR каблом усред вожње → ауто стане (застарео скен).',
        ],
      },
    ],
  },

  {
    slug: 'skolski-asistent-postavka',
    naziv: 'Школски асистент на Jetson Orin Nano',
    kratko: 'JetPack и CUDA, преузимање модела (Whisper, Qwen2-VL int4, Piper), C922 камера, RAG индекс и мерење.',
    nivo: 'напредно',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/skolski-asistent. Циљ радионице: ланац камера → говор → VLM → говор који ради потпуно офлајн на Jetson Orin Nano (8 GB).' },
      { type: 'h', text: 'Шта треба' },
      { type: 'specs', items: ['Jetson Orin Nano Developer Kit (8 GB)', 'NVMe SSD (модели су велики)', 'Logitech C922', 'активни хладњак и напајање 19 V', 'звучник или слушалице'] },
      { type: 'callout', tone: 'info', title: '„Super“ је софтвер, не други уређај', text: 'Jetson Orin Nano Developer Kit (8 GB) и „Orin Nano Super“ су иста плоча. JetPack 6.2 подиже такт и NPU са 40 на до 67 TOPS — довољан је најновији JetPack.' },
      { type: 'h', text: 'Систем (JetPack)' },
      {
        type: 'steps',
        items: [
          'Флешуј најновији JetPack (Ubuntu + CUDA + cuDNN + TensorRT) на NVMe преко SDK Manager-а или SD-Card Image алата.',
          'После првог подизања: sudo apt update && sudo apt full-upgrade -y.',
          'Провери да CUDA ради: nvcc --version и nvidia-smi (односно jetson_release).',
          'Укључи режим максималних перформанси.',
        ],
      },
      { type: 'code', lang: 'bash', code: 'sudo nvpmodel -m 0        # MAX-N режим\nsudo jetson_clocks         # закуцај фреквенције\ntegrastats                 # потрошња и заузеће, за мерења' },
      { type: 'h', text: 'Инсталација пројекта' },
      { type: 'code', lang: 'bash', code: 'git clone https://github.com/tspirot/edgeai.git\ncd edgeai/projekti/skolski-asistent\npython3 -m venv .venv && source .venv/bin/activate\npip install -e ".[kamera,zvuk,asr,vlm,tts]"' },
      {
        type: 'callout',
        tone: 'warn',
        title: 'torch на Jetson-у није са PyPI-ја',
        text: 'Инсталирај NVIDIA-ин torch/torchvision build за свој JetPack (jetson-ai-lab / форум). Обичан pip torch нема CUDA за ARM и VLM ће радити на процесору — преспоро.',
      },
      { type: 'h', text: 'Модели (једном, уз интернет)' },
      { type: 'code', lang: 'bash', code: 'asistent download-model --what all' },
      {
        type: 'ul',
        items: [
          'faster-whisper base (или small) → models/faster-whisper',
          'Qwen2-VL-2B-Instruct → models/vlm (int4 квантизација се ради при учитавању, bitsandbytes)',
          'Piper глас sr_RS-serbian-medium: .onnx и .onnx.json ручно у models/piper (huggingface.co/rhasspy/piper-voices)',
        ],
      },
      { type: 'h', text: 'Камера и микрофон' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања станице',
        caption:
          'Модели иду на NVMe, не на картицу — Qwen2-VL се учитава при сваком покретању и са картице то траје неупоредиво дуже.',
        data: {
          ploca: 'Jetson Orin Nano (8 GB)',
          veze: [
            { port: 'USB 3', ikona: '🎥', naziv: 'Logitech C922', detalj: 'слика и микрофон у једном' },
            { port: 'M.2', ikona: '💽', naziv: 'NVMe SSD', detalj: 'Whisper, Qwen2-VL, Piper, RAG' },
            { port: '3.5 mm', ikona: '🔊', naziv: 'Звучник', detalj: 'Piper изговара одговор' },
            { port: 'DP', ikona: '🖥️', naziv: 'Екран', detalj: 'исписан одговор уз говор' },
            { port: '19 V', ikona: '🔌', naziv: 'Напајање + хладњак', detalj: 'MAX-N режим тражи хлађење' },
          ],
        },
      },
      { type: 'code', lang: 'bash', code: 'asistent devices                 # индекс камере и микрофона\nv4l2-ctl --list-devices           # провера да систем види C922' },
      { type: 'p', text: 'У config.yaml постави camera.index и, за Jetson, asr.whisper.device: cuda и vlm.device: auto.' },
      { type: 'h', text: 'RAG над школским материјалима (опционо)' },
      { type: 'code', lang: 'bash', code: '# .txt и .md фајлови: приручници, стандарди, објашњења\nasistent index build materijali/\nasistent index show\nasistent ask --rag --image zadatak.jpg --question "Помози ми са овим задатком"' },
      { type: 'h', text: 'Провера — како знам да ради' },
      {
        type: 'steps',
        items: [
          'Без хардвера и модела: asistent ask --vlm dummy --asr dummy --tts console --image primer.jpg --question "Шта је ово?" — цео ланац одговори.',
          'Са моделима: покажи електричну шему, питај шта је елемент означен словом — одговор стигне за 2–4 s.',
          'Искључи мрежу (nmcli radio all off) и понови — мора да ради исто.',
          'Мери: asistent ask -v испише VLM латенцију; tegrastats у другом терминалу даје потрошњу.',
        ],
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Тачност се проверава, не претпоставља',
        text: 'Мали VLM греши. Направи скуп од 20–30 сопствених питања са познатим одговором и мери погодак са RAG-ом и без њега — то је резултат за Demo Day.',
      },
    ],
  },

  {
    slug: 'pirotski-cilim-postavka',
    naziv: 'Шара у духу пиротског ћилима на Jetson-у',
    kratko: 'Скуп података у радионици, правила клечања као кôд, SD 1.5 + ControlNet на Orin-у и картон за ткање који проверава ткаља.',
    nivo: 'напредно',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/pirotski-cilim. Циљ радионице: уређај који чита шару са ћилима и предлаже нову — а предлог избаци као картон за ткање који школски разбој може да изведе.' },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Прво правило: како се ово сме звати',
        text: '„Пиротски ћилим“ је од 2003. регистрована географска ознака. Право на то име имају само овлашћени произвођачи који раде по прописаном елаборату — вертикални разбој, техника клечања, вуна праменке за основу, прописане шаре и боје. Заштићено је име, не појединачан цртеж. Уређај зато свој излаз доследно зове „шара у духу пиротског ћилима“. То стоји у коду као cilim.OGRADA и има свој тест — ако неко промени формулацију, тест падне.',
      },
      { type: 'h', text: 'Шта треба' },
      { type: 'specs', items: ['Jetson Orin Nano Developer Kit (8 GB)', 'NVMe SSD (дифузиони модел је велик)', 'Logitech C922 изнад радне површине', 'екран на додир за скицу', 'дифузно осветљење са обе стране', 'приступ школској радионици ћилима'] },
      { type: 'h', text: 'Систем (JetPack)' },
      { type: 'code', lang: 'bash', code: 'sudo nvpmodel -m 0        # MAX-N режим\nsudo jetson_clocks         # закуцај фреквенције\ntegrastats                 # потрошња и заузеће, за мерења' },
      { type: 'h', text: 'Инсталација' },
      { type: 'code', lang: 'bash', code: 'git clone https://github.com/tspirot/edgeai.git\ncd edgeai/projekti/pirotski-cilim\npython3 -m venv .venv && source .venv/bin/activate\npip install -e ".[kamera,klasifikator,difuzija]"' },
      {
        type: 'callout',
        tone: 'warn',
        title: 'torch на Jetson-у није са PyPI-ја',
        text: 'Инсталирај NVIDIA-ин torch build за свој JetPack (jetson-ai-lab). Обичан pip torch нема CUDA за ARM, па би дифузија радила на процесору — минутима по слици уместо секундама.',
      },
      { type: 'h', text: 'Прво покретање — без иједног модела' },
      { type: 'p', text: 'Пре него што се ишта преузме, цео ланац већ ради. Режим pravila гради шару искључиво из правила заната, без мреже. Он је уједно и мерило: ако дифузиони модел не даје бољи резултат од овога, не вреди својих петнаест вати.' },
      { type: 'code', lang: 'bash', code: 'cilim motivi --sve\ncilim smisli --generator pravila --motiv kornjaca --seed 7 -o izlaz/\n# izlaz/: sara.png, karton.csv, karton.png' },
      { type: 'h', text: 'Правила заната — шта тачно проверава' },
      {
        type: 'ul',
        items: [
          'Пет појасева: ресе, спољашњи ћенар, бордура, унутрашњи ћенар, поље.',
          'Симетрија: шара се гради огледањем и понављањем.',
          'Два лица: клечање даје оба лица потпуно иста, па нема пловећих нити — свака боја мора да стоји у довољно дугом потезу.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Мери се на картону, не на пикселима',
        text: 'Потез је оно што ткаља отка у једном маху, а то је ћелија картона — не пиксел. Ситан детаљ лако прође проверу на слици пуне резолуције а падне на разбоју. Зато и генератор ради на мрежи картона, и провера. Ако ткаља каже да су предлози преситни, подигни pravila.min_niti.',
      },
      { type: 'h', text: 'Скуп података правите ви' },
      {
        type: 'steps',
        items: [
          'Сними ћилиме у радионици: камера право надоле, светло са обе стране кроз дифузор.',
          'Сваку шару сними са више ћилима — иначе модел научи ћилим, а не шару.',
          'Забележи чији је ћилим и да ли је власник дао сагласност.',
          'Означи исечке у Label Studio-у; класе су id из cilim/motivi.yaml.',
          'Прођи каталог са неким ко тка и тек тада постави potvrdila_radionica: true.',
          'Дообучи ViT на рачунару са GPU; тежине носе и списак класа, да модел не проговори туђа имена.',
        ],
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Каталог још нико није потврдио',
        text: 'Шеснаест назива у cilim/motivi.yaml преузето је из Националног регистра, Википедије и литературе — ниједан није прошао радионицу. Програм зато уз свако значење исписује ограду „НЕПОТВРЂЕНО“. Уклонити је сме само онај ко тка.',
      },
      { type: 'h', text: 'Шема повезивања' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Станица поред разбоја',
        caption:
          'Екран је овде и улаз и излаз — на њему ученик црта скицу коју ControlNet држи као ограничење. Зато мора бити на додир.',
        data: {
          ploca: 'Jetson Orin Nano (8 GB)',
          veze: [
            { port: 'USB 3', ikona: '🎥', naziv: 'Logitech C922', detalj: 'ћилим и скица, поглед надоле' },
            { port: 'M.2', ikona: '💽', naziv: 'NVMe SSD', detalj: 'SD 1.5, ControlNet, LoRA' },
            { port: 'DP', ikona: '🖐️', naziv: 'Екран на додир', detalj: 'скица улази, шара излази' },
            { port: 'USB', ikona: '🖨️', naziv: 'Штампач', detalj: 'картон за ткање на папиру' },
            { port: '19 V', ikona: '🔌', naziv: 'Напајање и хладњак', detalj: 'MAX-N режим тражи хлађење' },
          ],
        },
      },
      { type: 'h', text: 'Провера — како знам да ради' },
      {
        type: 'steps',
        items: [
          'Без модела: cilim smisli --generator pravila --seed 7 — испис мора рећи „изводљиво“ и 0 кратких потеза.',
          'Са моделима: cilim smisli --skica skica.png --motiv sofra — предлог за неколико секунди.',
          'Искључи мрежу (nmcli radio all off) и понови — мора да ради исто.',
          'Одштампај karton.png и однеси га ткаљи. То је права провера.',
          'Мери: cilim smisli -v за кашњење, tegrastats у другом терминалу за потрошњу.',
        ],
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Мера успеха није лепота слике',
        text: 'Модел лако нацрта шару коју је немогуће исктати. Бројка за Demo Day је колико је предложених картона ткаља прогласила изводљивим — не колико слика изгледа лепо на екрану.',
      },
    ],
  },

  {
    slug: 'dvojnik-postavka',
    naziv: 'Двојник: окретни сто, скенирање и штампа',
    kratko: 'Склапање окретног стола, мерење геометрије камере, снимање круга кадрова, резбарење воксела на Orin-у и STL за штампач.',
    nivo: 'напредно',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/dvojnik. Циљ радионице: посетилац стави предмет на сто, а после минут ноду има STL који школски штампач одштампа.' },
      {
        type: 'callout',
        tone: 'info',
        title: 'Прво покрени без ичега',
        text: 'Цео ланац ради у симулацији, на телу задатом формулом. Пре него што склопиш иједан кабл, покрени `dvojnik sim --telo kugla --mera 60` и погледај STL. Тако знаш да математика ради, па све што после пукне долази од хардвера.',
      },
      { type: 'h', text: 'Шта треба' },
      { type: 'specs', items: ['Jetson Orin Nano Developer Kit (8 GB)', 'Logitech C922 на непомичном сталку', 'корачни мотор 28BYJ-48 + ULN2003 драјвер', 'плоча стола из 3D штампе', 'матирана позадина у контрастној боји', 'дифузно осветљење са обе стране', 'шублер', '3D штампач'] },
      { type: 'h', text: 'Окретни сто' },
      { type: 'p', text: 'Због њега систем зна угао сваког кадра уместо да га процењује. Мотор 28BYJ-48 има 4096 полукорака по кругу, што је 0,088° по кораку — далеко финије него што треба за 120 кадрова.' },
      { type: 'code', lang: 'bash', code: '# ULN2003 IN1–IN4 на GPIO 18, 23, 24, 25 (BCM)\n# Мотор има СВОЈЕ напајање 5 V — не вуци га са плоче\ndvojnik sto --stepeni 360      # мора да се врати тачно где је почео' },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Ако сто не стигне до краја круга',
        text: 'Мотор прескаче кораке кад је оптерећен или кад је пауза између корака прекратка. Смањи тежину на столу, провери напајање мотора и не смањуј паузу испод 1,5 ms. Прескочен корак значи да је угао кадра погрешан — а на томе цео метод стоји.',
      },
      { type: 'h', text: 'Мерење геометрије камере' },
      { type: 'p', text: 'Ово је најдосаднији и најважнији корак. Из ове четири бројке се рачуна пројекција, па погрешно растојање даје модел погрешног ОБЛИКА, не само величине.' },
      { type: 'code', lang: 'yaml', code: 'kamera:\n  vfov: 42.0            # усправно видно поље објектива, степени\n  rastojanje: 300.0     # mm, од осе стола до објектива\n  visina_kamere: 220.0  # mm, објектив изнад површине стола\n  cilj: 60.0            # mm, висина тачке у коју камера гледа, на оси' },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Камера се после овога НЕ помера',
        text: 'Ни за милиметар, ни између кадрова, ни између снимања. Закључај и аутофокус и аутоекспозицију — ако се слика мења сама од себе, одузимање позадине ће ту промену пријавити као део предмета.',
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Поставка',
        caption:
          'Камера гледа сто са стране, мало одозго — тако види и обрис и горњу ивицу. Што је ближа висини предмета, то мање прецењује висину; сав остали посао обави ротација.',
        data: {
          kamera: { naziv: 'Камера са стране', vfov: 42, visina: '≈ 22 cm' },
          zone: [
            { naziv: 'Радни простор — коцка воксела', od: 34, do: 70 },
          ],
          objekti: [
            { ikona: '💡', naziv: 'Светло лево', x: 16, y: 44 },
            { ikona: '🗿', naziv: 'Предмет', x: 50, y: 52 },
            { ikona: '💡', naziv: 'Светло десно', x: 84, y: 44 },
            { ikona: '🎞️', naziv: 'Позадина', x: 50, y: 20 },
          ],
          tlo: 'Сто за скенирање — поглед одозго',
        },
      },
      { type: 'h', text: 'Снимање и склапање' },
      { type: 'code', lang: 'bash', code: 'dvojnik snimi --kadrova 120 -o snimak/\n# 1) склони предмет → снима празну позадину\n# 2) стави предмет на средину → снима круг\n\ndvojnik slozi snimak/ --visina-mm 84.5 -o izlaz/   # висина са шублера' },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Без шублера нема праве величине',
        text: 'Из слика се добија облик, не мере. Док се не унесе једна измерена дужина, модел може бити и напрстак и буре — програм на то и упозорава у испису. Једна измерена бројка вреди више од сто кадрова.',
      },
      { type: 'h', text: 'Две границе методе' },
      {
        type: 'ul',
        items: [
          'Удубљења остају пуна — унутрашњост шоље се са стране не види као рупа, па се не може ни одрезати.',
          'Висина се благо прецени — сви кадрови су са исте висине камере. Водоравне мере су тесне.',
          'Обе су проверене тестовима у репоу, не остављене као напомена.',
          'Ко хоће тесну висину: сними два круга, са две висине камере.',
        ],
      },
      { type: 'h', text: 'Провера — како знам да ради' },
      {
        type: 'steps',
        items: [
          'Без хардвера: dvojnik sim --telo kugla --mera 60 → габарит мора испасти око 60 mm.',
          'Стави познат предмет (коцкицу коју си сам одштампао) и скенирај је — упореди са цртежом.',
          'Одштампај двојника и стави оба на шублер. Одступање у милиметрима је твој резултат.',
          'Мери време: dvojnik sim -v, уз tegrastats у другом терминалу.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'GPU без иједног неурона',
        text: 'Резбарење је 500 милиона независних пројекција — тачно оно за шта су CUDA језгра направљена, а неуронске мреже нигде нема. Прво измери време на процесору, па тек онда пребаци на GPU: без тог првог броја убрзање нема смисла. Упутство је у projekti/dvojnik/docs/na-jetsonu.md.',
      },
    ],
  },

  {
    slug: 'ziva-rec-postavka',
    naziv: 'Жива реч: снимање и препис пиротског говора',
    kratko: 'JetPack и Whisper, мерење торлачних црта, сесија снимања код говорника, исправка и корпус са сагласношћу.',
    nivo: 'напредно',
    vreme: 'радионица + терен',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Кôд је у монорепоу, фасцикла projekti/ziva-rec. Циљ: станица која се носи код говорника, сними како прича, транскрибује на лицу места и одмах да да се исправи — све офлајн.' },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Ово прикупља грађу, не прави бота',
        text: 'Чет-бот који „зна“ пиротски је засебан, каснији веб пројекат. Мали модел са мало података измишља дијалекат, а код угроженог језика то није безазлено. Права вредност је корпус који настаје, не модел.',
      },
      { type: 'h', text: 'Прво покрени без ичега' },
      { type: 'code', lang: 'bash', code: 'cd edgeai/projekti/ziva-rec\npython3 -m venv .venv && source .venv/bin/activate\npip install -e .\n\ngovor oceni "Съга че идем да купим лебац"   # оцена реченице\ngovor prepisi snimak.wav --asr dummy         # цео ланац без модела' },
      { type: 'h', text: 'Систем и модел (Jetson)' },
      { type: 'code', lang: 'bash', code: 'sudo nvpmodel -m 0 && sudo jetson_clocks\npip install -e ".[zvuk,asr]"\ngovor download-model            # Whisper large-v3-turbo, једном уз интернет' },
      {
        type: 'callout',
        tone: 'warn',
        title: 'torch/CTranslate2 на Jetson-у',
        text: 'faster-whisper тражи CTranslate2 build за ARM са CUDA. Узми га из NVIDIA-иног канала или jetson-ai-lab; обичан pip даје CPU верзију, преспору за терен.',
      },
      { type: 'h', text: 'Мерење торлачности' },
      { type: 'p', text: 'Модул crte.py мери колико је реченица дијалекатска преко правила: полугласник (със, съга), /ѕ/, аналитички компаратив (по-убав), постпозитивни члан (човекат, детето), изгубљено /х/ (леб, оћу), аорист, футур са „че“. Намерно је груб — служи да се издвоје јако дијалекатски сегменти и да се провери да дообучени Whisper није „упеглао“ говор.' },
      { type: 'code', lang: 'bash', code: 'govor oceni "Данас ћу отићи у град да купим хлеб"   # скор ~0.09\ngovor oceni "Съга че идем да купим лебац, море"      # скор 1.00' },
      { type: 'h', text: 'Сесија снимања' },
      {
        type: 'steps',
        items: [
          'Објасни говорнику шта се снима и зашто — да се сачува пиротски говор.',
          'Сними реченицу у којој говорник каже да пристаје — то је сагласност.',
          'govor korpus govornik baba-mara --inicijali "М. Ј." --selo Крупац --godiste 193x --saglasnost',
          'govor ispravi snimak.wav --govornik baba-mara — станица нуди сегмент по сегмент.',
          'Enter = препис тачан, . = прескочи, укуцан текст = исправка.',
          'govor korpus odobri <id> — тек кад је говорник видео и одобрио.',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Ниједан кабл не иде ка мрежи — то је суштина пројекта, не штедња. Микрофон бира се пре камере: за старије гласове важнији је.',
        data: {
          ploca: 'Jetson Orin Nano (8 GB)',
          veze: [
            { port: 'USB', ikona: '🎙️', naziv: 'USB микрофон', detalj: '16 kHz, глас говорника' },
            { port: '3.5 mm', ikona: '🎧', naziv: 'Слушалице', detalj: 'говорник слуша свој снимак' },
            { port: 'DP', ikona: '✍️', naziv: 'Екран за исправку', detalj: 'сегмент по сегмент' },
            { port: 'M.2', ikona: '💽', naziv: 'NVMe SSD', detalj: 'Whisper и корпус' },
            { port: 'USB-C', ikona: '🔋', naziv: 'Повербанк', detalj: 'терен, без мреже' },
          ],
        },
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Сагласност, приватност, право на брисање',
        text: 'Само иницијали и село, деценија рођења уместо датума. Говорник у сваком тренутку може да каже „избришите то“. Извоз за дообуку прескаче све без сагласности — то је капија, не филтер. Детаљно у projekti/ziva-rec/docs/etika.md.',
      },
      { type: 'h', text: 'Дообука и провера' },
      {
        type: 'steps',
        items: [
          'govor korpus stanje — прати „sati_odobreno“ и „prosecan_skor“.',
          'govor korpus izvoz -o parovi.tsv — (wav, текст) само одобрено и са сагласношћу.',
          'Дообука Whisper-а (LoRA) на рачунару са GPU, подела по говорницима не по исечцима.',
          'После дообуке: упореди просечан скор торлачности пре и после. Ако је пао, модел је померен ка стандарду — то је грешка, не напредак.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Постоји подлога',
        text: 'Златковићев „Речник пиротског говора“ (~33.000 речи), говорни корпус торлачког, Torlak ReLDI означивач, рад Tang & Vuković (COLING 2025). Приче Мијалка Расничког су објављена пиротска проза која, уз дозволу, може да засеје корпус. Упутство за дообуку: projekti/ziva-rec/docs/doobuka.md.',
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Прикупљање података ЈЕСТЕ пројекат',
        text: 'Тражи сагласност, стрпљење кроз месеце и људе који стварно говоре пиротски да проверавају. Ако то нема ко да води, боље не почети — половичан корпус угроженог језика гори је од никаквог.',
      },
    ],
  },

  {
    slug: 'demo-day',
    naziv: 'Припрема за Demo Day',
    kratko: 'Шта треба да ради, како се показује и шта се мери — контролна листа пред јавну презентацију.',
    nivo: 'основно',
    vreme: 'радионица',
    sadrzaj: [
      { type: 'p', lead: true, text: 'Demo Day је јавна презентација прототипова у Пироту, у сарадњи са ZIP Центром. Циљ: свака станица има демо који публика разуме за 30 секунди.' },
      { type: 'h', text: 'Контролна листа по станици' },
      {
        type: 'ul',
        items: [
          'Уређај се подиже сам, без тастатуре и миша (autostart сервис).',
          'Ради без интернета — провери на лицу места, у авионском режиму.',
          'Једна реченица објашњења на плочи изнад станице.',
          'Резервно напајање и резервна SD картица.',
          'Бројке: тачност, кашњење, кадрови у секунди — на графикону, не напамет.',
        ],
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Распоред станице',
        caption:
          'Посетилац прилази с фронта, плоча са једном реченицом стоји изнад уређаја, а екран са бројкама гледа према публици. Резервно напајање је иза стола, не преко пута пролаза.',
        data: {
          kamera: { naziv: 'Уређај са сензором', vfov: 70, visina: 'ниво стола' },
          zone: [
            { naziv: 'Простор за посетиоца — демо од 30 s', od: 40, do: 82 },
          ],
          objekti: [
            { ikona: '📊', naziv: 'Екран са бројкама', x: 20, y: 18 },
            { ikona: '🪧', naziv: 'Плоча с објашњењем', x: 78, y: 18 },
            { ikona: '🧑', naziv: 'Посетилац', x: 50, y: 66 },
          ],
          tlo: 'Сто станице — поглед одозго',
        },
      },
      { type: 'h', text: 'Прича за медије' },
      {
        type: 'p',
        text: 'Свака станица везана за Пирот: прелаз код школе, Стара планина, пиротска гума и текстил, приступачност за суграђане. То је оно што медији преносе.',
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Демо који не пукне',
        text: 'Не ослањај се на Wi-Fi у сали. Не ослањај се на јако осветљење. Пробај демо тачно у условима у којима ће се одвијати.',
      },
    ],
  },
]

export const getUputstvo = (slug) => uputstva.find((u) => u.slug === slug)
