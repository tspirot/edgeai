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
