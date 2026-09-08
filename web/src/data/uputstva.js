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
