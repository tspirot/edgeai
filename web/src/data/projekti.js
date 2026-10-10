/* Пројекти програма „Edge AI: Наука у петој брзини“ (Техничка школа Пирот).
   `pozicija` је координата чвора у 3D сцени на насловној страни. */

export const projekti = [
  {
    slug: 'titlovi-uzivo',
    broj: '01',
    naziv: 'Титлови уживо, без облака',
    ikona: '🎙️',
    kratko:
      'Препознавање говора на српском које ради на самом уређају и исписује титлове у реалном времену — за ученике оштећеног слуха.',
    status: 'у изради',
    boja: '#4ED8A3',
    cvor: 'Титлови уживо',
    pozicija: [-3.2, 0.98, 0.99],
    hardver: ['Raspberry Pi 5', 'USB микрофон', 'HDMI пројекција'],
    tehnologije: ['faster-whisper', 'LocalAgreement стриминг', 'пресловљавање'],
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/titlovi-uzivo',
    uputstvo: 'titlovi-uzivo-instalacija',
    telemetrija: {
      latencija: '~320 ms',
      npuCpu: 'Pi 5 Quad A76 (int8)',
      potrosnja: '~5.2 W',
      offline: '100% Офлајн',
      memorija: '420 MB RAM',
      model: 'faster-whisper small-int8',
    },
    pipeline: [
      { icon: '🎙️', title: 'USB микрофон', detail: '16 kHz моно звук, 100 ms сегменти' },
      { icon: '⚡', title: 'VAD детектор', detail: 'Одвајање говора од шума учионице' },
      { icon: '🧠', title: 'Whisper int8', detail: 'Локална инференца на Pi 5 CPU' },
      { icon: '🎯', title: 'LocalAgreement', detail: 'Поређење хипотеза без треперења' },
      { icon: '🖥️', title: 'HDMI пројекција', detail: 'Ћирилични титлови за слушаоце' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Уређај слуша излагање и на пројектору исписује титлове док говорник још говори. Исти посао који обично тражи облак и слање гласа на туђи сервер овде се ради локално — уз приватност и без кашњења.',
      },
      { type: 'h', text: 'Зашто је ово најјачи доказ програма' },
      {
        type: 'p',
        text:
          'Говор у текст је услуга коју данас нуде велике компаније преко интернета. Ми исту ствар радимо на плочи од 90 грама, без мреже. На Demo Day-у уређај титлује баш то излагање које траје — публика одмах разуме шта види.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'Микрофон снима звук у блоковима од 100 ms (16 kHz, моно).',
          'Једноставан детектор говора одваја речи од тишине и препознаје крај реченице.',
          'Whisper модел (faster-whisper, int8) се сваких ~1,5 s покреће на растућем прозору звука.',
          'Реч се проглашава потврђеном тек кад се појави у две узастопне хипотезе (LocalAgreement) — тако титл не „трепери“.',
          'Текст се пресловљава у ћирилицу и приказује преко pygame-а на HDMI излазу или у прегледачу на локалној мрежи.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Ништа не напушта учионицу',
        text:
          'Модел се преузме једном, после тога систем ради потпуно офлајн. Звук се нигде не снима нити шаље.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'Raspberry Pi 5 (8 GB)',
          'USB камера са микрофоном',
          'Активни хладњак',
          'HDMI пројектор или монитор',
          'AI HAT+ (опционо)',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Микрофон улази преко USB-а, титл излази преко HDMI-ја. Мрежни кабл служи само за прво преузимање модела — после тога се може извући.',
        data: {
          ploca: 'Raspberry Pi 5 (8 GB)',
          veze: [
            { port: 'USB', ikona: '🎙️', naziv: 'USB микрофон', detalj: '16 kHz моно, 100 ms сегменти' },
            { port: 'HDMI', ikona: '🖥️', naziv: 'Пројектор или монитор', detalj: 'ћирилични титлови уживо' },
            { port: 'USB-C', ikona: '🔌', naziv: 'Напајање 27 W', detalj: 'обавезно за пун такт' },
            { port: 'GPIO', ikona: '🌀', naziv: 'Активни хладњак', detalj: 'без њега процесор успорава' },
          ],
        },
      },
      {
        type: 'p',
        text:
          'Whisper на Raspberry Pi 5 ради на процесору. AI HAT+ са Hailo-8L чипом користе пројекти са сликом (детекција објеката); за говор он засад није неопходан.',
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Уживо титловање говора са бине, пројектовано изнад говорника.',
          'Пребацивач ћирилица / латиница и величина фонта.',
          'Кратак филм „како то ради“ са графиконом кашњења.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Пројекат директно циља приступачност — часови и јавни догађаји доступни ученицима и грађанима оштећеног слуха, без претплате и без интернета.',
      },
    ],
  },

  {
    slug: 'pametna-zebra',
    broj: '02',
    naziv: 'Паметна зебра',
    ikona: '🚗',
    kratko:
      'Камера изнад пешачког прелаза броји пешаке, прати возила и пали упозорење када се пешак и возило приближавају истовремено.',
    status: 'предлог',
    boja: '#E5B842',
    cvor: 'Паметна зебра',
    pozicija: [-2.82, -2.5, -0.87],
    hardver: ['Raspberry Pi 5', 'AI HAT+ Hailo-8L', 'Camera Module 3', 'Сет 37 у 1'],
    tehnologije: ['YOLOv8n', 'ByteTrack', 'LED упозорење', 'GPIO актуација'],
    uputstvo: 'ai-hat-hailo',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/pametna-zebra',
    telemetrija: {
      latencija: '28 ms / кадру',
      npuCpu: 'Hailo-8L (13 TOPS)',
      potrosnja: '~6.1 W',
      offline: '100% Офлајн',
      fps: '30 FPS',
      model: 'YOLOv8n + ByteTrack',
    },
    pipeline: [
      { icon: '📷', title: 'Camera Module 3', detail: 'Full HD снимак прелаза испред школе' },
      { icon: '⚡', title: 'Hailo-8L NPU', detail: 'YOLOv8n детекција пешака и возила' },
      { icon: '🎯', title: 'ByteTrack', detail: 'Праћење трајекторија и вектори брзине' },
      { icon: '📐', title: 'Геометријски процесор', detail: 'Прорачун тачке и времена пресека' },
      { icon: '🚦', title: 'Семафор & Аларм', detail: 'RGB LED, зујалица и релеј из сета 37 у 1' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Камера код школе гледа пешачки прелаз. Локално, на уређају, броји пешаке и возила и процењује брзину. Када се путеви пешака и возила секу у истом тренутку, пали светлосно упозорење.',
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Приватност уграђена у дизајн',
        text:
          'Ништа се не снима нити шаље. Уређај памти само бројеве: колико пешака, колико возила, у ком временском интервалу.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'YOLOv8n детектује пешаке и возила у сваком кадру (инференца на Hailo-8L акцелератору).',
          'ByteTrack повезује детекције кроз време у путање.',
          'Из путање се процењује смер и брзина; једноставна геометрија рачуна време до тачке пресека.',
          'Ако је време мање од прага — пали се упозорење из сета „37 у 1“.',
        ],
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Поставка на терену',
        caption:
          'Камера гледа низ прелаз, а не у лица — из те висине и угла добија се путања, не портрет. Зона упозорења почиње довољно рано да возач стигне да реагује.',
        data: {
          kamera: { naziv: 'Камера изнад прелаза', vfov: 66, visina: '≈ 4 m' },
          zone: [
            { naziv: 'Зона упозорења возача', od: 8, do: 42 },
            { naziv: 'Пешачки прелаз', od: 48, do: 78 },
          ],
          objekti: [
            { ikona: '🚗', naziv: 'Возило', x: 34, y: 24 },
            { ikona: '🚶', naziv: 'Пешак', x: 68, y: 62 },
            { ikona: '💡', naziv: 'LED', x: 16, y: 20 },
          ],
          tlo: 'Улица испред школе — поглед одозго',
        },
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Камера иде на CSI прикључак плоче, а акцелератор на PCIe преко FPC кабла — не на GPIO пинове за податке.',
        data: {
          ploca: 'Raspberry Pi 5',
          veze: [
            { port: 'PCIe', ikona: '⚡', naziv: 'AI HAT+ (Hailo-8L)', detalj: '13 TOPS, детекција у кадру' },
            { port: 'CSI', ikona: '📷', naziv: 'Camera Module 3', detalj: 'Full HD, поглед на прелаз' },
            { port: 'GPIO', ikona: '🚦', naziv: 'Семафор & Аларм', detalj: 'RGB LED, зујалица и релеј из сета 37 у 1' },
            { port: 'USB-C', ikona: '🔌', naziv: 'Напајање 27 W', detalj: 'плоча и акцелератор заједно' },
          ],
        },
      },
      { type: 'h', text: 'Додатак: Хардверска надградња са сетом „37 у 1” 🚦' },
      {
        type: 'p',
        text:
          'Када основни софтверски ланац проради у симулацији или са обичном камером, на Raspberry Pi 5 се могу везати модули из школског сензорског сета „37 у 1” за пуну физичку сигнализацију на макети пешачког прелаза:',
      },
      {
        type: 'steps',
        items: [
          'RGB LED (KY-016 / KY-011) — динамички семафор: зелено (слободан прелаз), жуто (возило у зони прилаза), црвено трепћуће (опасност када је TTC < 3 s).',
          'Активна зујалица (Buzzer KY-012) — испрекидани звучни аларм за пешаке и возаче у моменту критичног приближавања.',
          '5V Релеј (KY-019) — аутоматско укључивање јачег спољног LED рефлектора за осветљење прелаза ноћу.',
          'LDR фотоотпорник (KY-018) — сензор амбијенталног светла: рефлектор преко релеја се активира само када падне мрак.',
        ],
      },
      { type: 'h3', text: 'Шема повезивања (40-pin GPIO на Raspberry Pi 5)' },
      {
        type: 'code',
        lang: 'text',
        code: `        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power ────────► [VCC] 5V Релеј (KY-019)
               │ ●  ● │(Pin 4)  5V Power
   GND  (Pin 6)│ ●  ● │(Pin 5)
               │ ●  ● │(Pin 9)  GND ─────────────► [GND] Заједничка маса свих модула
GPIO 17 (Pin 11)│ ●  ● │(Pin 12)
GPIO 27 (Pin 13)│ ●  ● │(Pin 14)
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [S / IN] Активна зујалица (KY-012)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [IN] 5V Релеј (KY-019)
               │ ●  ● │(Pin 20) GND
GPIO 25 (Pin 22)│ ●  ● │(Pin 21)
               └──────────────┘

  Детаљна веза сигнала:
  ├── RGB LED (KY-016):
  │     ├── Pin 'R' (Црвена)   ──► GPIO 17  (Pin 11)
  │     ├── Pin 'G' (Зелена)   ──► GPIO 27  (Pin 13)
  │     ├── Pin 'B' (Плава)    ──► GPIO 22  (Pin 15)
  │     └── Pin '-' (GND)      ──► Заједнички GND (Pin 9 или 20)
  │
  ├── Активна зујалица (KY-012):
  │     ├── Pin 'S' (Сигнал)   ──► GPIO 23  (Pin 16)
  │     └── Pin '-' (GND)      ──► Заједнички GND
  │
  ├── 5V Релеј (KY-019):
  │     ├── Pin 'VCC'          ──► 5V  (Pin 2)
  │     ├── Pin 'GND'          ──► GND (Pin 6 или 20)
  │     └── Pin 'IN'           ──► GPIO 24  (Pin 18)
  │
  └── LDR сензор светла са компаратором (KY-018):
        ├── Pin 'VCC'          ──► 3.3V (Pin 1)  [ПАЖЊА: не на 5V због Pi 5 GPIO!]
        ├── Pin 'GND'          ──► GND
        └── Pin 'DO' (Digital) ──► GPIO 25  (Pin 22)`,
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Важно за Raspberry Pi 5',
        text:
          'Сви сигнални pin-ови на Pi 5 раде искључиво на 3.3V логици. LDR модул обавезно везујте на 3.3V (Pin 1). Релеј модул користи 5V за напајање шпулне, али његов контролни улаз (IN) безбедно окида са 3.3V логичким нивоом.',
      },
      { type: 'h3', text: 'Пример кода за проширење (без мењања постојећег кода)' },
      {
        type: 'p',
        text: 'Ученици могу додати класу у src/zebra/io/hardware_upgrade.py:',
      },
      {
        type: 'code',
        lang: 'python',
        code: `"""Проширена контрола хардвера из сета 37 у 1 за Паметну зебру."""
from __future__ import annotations
import logging

log = logging.getLogger(__name__)

class SmartZebraHardware:
    """Управља RGB семафором, зујалицом, LDR-ом и релејем за рефлектор."""

    def __init__(
        self,
        pin_r: int = 17,
        pin_g: int = 27,
        pin_b: int = 22,
        pin_buzzer: int = 23,
        pin_relay: int = 24,
        pin_ldr: int = 25,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._led = None
        self._buzzer = None
        self._relay = None
        self._ldr = None

        if not enabled:
            return

        try:
            from gpiozero import RGBLED, Buzzer, OutputDevice, DigitalInputDevice

            self._led = RGBLED(red=pin_r, green=pin_g, blue=pin_b, active_high=True)
            self._buzzer = Buzzer(pin_buzzer)
            self._relay = OutputDevice(pin_relay, active_high=True, initial_value=False)
            self._ldr = DigitalInputDevice(pin_ldr)

            log.info("Хардвер из сета 37 у 1 успешно иницијализован.")
            self.set_status("safe")
        except Exception as exc:
            log.warning("Хардвер недоступан (%s) — прелаз у софтверски симулатор.", exc)
            self.enabled = False

    def is_dark(self) -> bool:
        """Враћа True ако је LDR очитао низак ниво амбијенталног светла."""
        return bool(self._ldr and self._ldr.is_active)

    def set_status(self, level: str) -> None:
        """Поставља стање семафора: 'safe', 'caution', или 'danger'."""
        if not self.enabled:
            return

        # 1. Ноћни рефлектор преко релеја
        if self._relay:
            if self.is_dark() and level in ("caution", "danger"):
                self._relay.on()
            elif not self.is_dark():
                self._relay.off()

        # 2. Светлосна и звучна сигнализација
        if level == "danger":
            if self._led:
                self._led.color = (1, 0, 0)      # Црвено
            if self._buzzer:
                self._buzzer.beep(on_time=0.1, off_time=0.1)  # Испрекидани аларм
        elif level == "caution":
            if self._led:
                self._led.color = (1, 0.7, 0)    # Жуто
            if self._buzzer:
                self._buzzer.off()
        else:  # safe
            if self._led:
                self._led.color = (0, 1, 0)      # Зелено
            if self._buzzer:
                self._buzzer.off()

    def close(self) -> None:
        for dev in (self._led, self._buzzer, self._relay, self._ldr):
            if dev: dev.close()`,
      },
      { type: 'h3', text: 'Брзи тест на плочи' },
      {
        type: 'code',
        lang: 'bash',
        code: `python -c "
from gpiozero import RGBLED, Buzzer; import time
led = RGBLED(17, 27, 22); b = Buzzer(23)
print('Зелено...'); led.color = (0, 1, 0); time.sleep(1)
print('Жуто...'); led.color = (1, 0.7, 0); time.sleep(1)
print('Црвено + аларм...'); led.color = (1, 0, 0); b.beep(0.1, 0.1, n=5); time.sleep(1)
led.close(); b.close()
"`,
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Жива слика са бројачем пешака и возила.',
          'Дневни график саобраћаја испред школе.',
          'Извештај који има смисла предати граду.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Реалан скуп података о саобраћају на конкретном прелазу код школе — основа за разговор са локалном самоуправом о безбедности.',
      },
    ],
  },

  {
    slug: 'cuvar-stare-planine',
    broj: '03',
    naziv: 'Чувар Старе планине',
    ikona: '🌲',
    kratko:
      'Фотозамка која на лицу места препознаје животињску врсту и бележи температуру, влажност и квалитет ваздуха — без сигнала и без интернета.',
    status: 'предлог',
    boja: '#52B788',
    cvor: 'Чувар Старе планине',
    pozicija: [-1.4, 1.75, 2.06],
    hardver: ['Raspberry Pi 5', 'AI Camera IMX500', 'BME688', 'Сет 37 у 1'],
    tehnologije: ['класификација врста', 'рад на батерији', 'инференца на сензору', 'Wake-on-event'],
    uputstvo: 'ai-camera-imx500',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/cuvar-stare-planine',
    telemetrija: {
      latencija: '18 ms',
      npuCpu: 'IMX500 сензорски NPU',
      potrosnja: '~1.8 W (sleep)',
      offline: '100% Офлајн',
      baterija: 'до 7 дана на терену',
      model: 'MobileNetV4 + BME688',
    },
    pipeline: [
      { icon: '📷', title: 'IMX500 сензор', detail: 'Аутономна детекција покрета на чипу' },
      { icon: '🧠', title: 'Инференца на сензору', detail: 'Препознавање врсте док Pi процесор спава' },
      { icon: '🌡️', title: 'BME688 мерачи', detail: 'Температура, влажност, VOC честице' },
      { icon: '🚨', title: 'Теренска заштита', detail: 'IR wake-up и тампер сензор ударца' },
      { icon: '💾', title: 'microSD логер', detail: 'Уписивање само значајних налаза' },
      { icon: '📊', title: 'Еколошка база', detail: 'Локални архив биодиверзитета' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Уређај на терену. Када нешто прође испред камере, мрежа која се извршава на самом IMX500 сензору препозна о којој се врсти ради и сними само тај кадар. Уз то мери климу и квалитет ваздуха.',
      },
      { type: 'h', text: 'Зашто IMX500' },
      {
        type: 'p',
        text:
          'Код IMX500 камере неуронска мрежа ради на чипу сензора, па главни процесор већину времена спава. Потрошња је мала — уређај ради на батерији данима, а картица траје јер се снима само оно што је препознато.',
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Мери, не прича',
        text:
          'Пројекат даје бројке о биодиверзитету и галерију снимака, уместо општих прича о заштити природе.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'BME688 иде на I²C — две линије података плус напајање. IMX500 на CSI прикључку ради инференцу сам, па главни процесор већину времена спава.',
        data: {
          ploca: 'Raspberry Pi 5',
          veze: [
            { port: 'CSI', ikona: '📷', naziv: 'AI Camera IMX500', detalj: 'мрежа ради на самом сензору' },
            { port: 'I²C', ikona: '🌡️', naziv: 'BME688', detalj: 'температура, влажност, VOC' },
            { port: 'GPIO', ikona: '🐾', naziv: 'IR & Тампер сензори', detalj: 'Wake-on-event и заштита од обарања' },
            { port: 'USB-C', ikona: '🔋', naziv: 'Батерија / power bank', detalj: 'до 7 дана уз спавање' },
          ],
        },
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Поставка на терену',
        caption:
          'Фотозамка се веже за стабло на висини крупније дивљачи и гледа попреко на стазу — тако животиња прође кроз кадар, а не право у објектив.',
        data: {
          kamera: { naziv: 'Фотозамка на стаблу', vfov: 58, visina: '≈ 1,2 m' },
          zone: [
            { naziv: 'Зона окидања', od: 22, do: 70 },
          ],
          objekti: [
            { ikona: '🦌', naziv: 'Дивљач', x: 30, y: 46 },
            { ikona: '🌲', naziv: 'Стаза', x: 74, y: 58 },
          ],
          tlo: 'Стаза на Старој планини — поглед одозго',
        },
      },
      { type: 'h', text: 'Додатак: Хардверска надградња са сетом „37 у 1” 🌲' },
      {
        type: 'p',
        text:
          'У основном режиму фотозамка се ослања на софтверску детекцију промене кадра. У теренским условима Старе планине, где је трајање батерије кључно, уређај се може надградити сензорима из школског сета „37 у 1”:',
      },
      {
        type: 'steps',
        items: [
          'IR сензор препрека / покрета (KY-032 / TCRT5000 KY-033) — хардверски Wake-up окидач: тренутно буди камеру када дивљач пресече сноп, чиме штеди батерију.',
          'Сензор вибрације и ударца (KY-002 / KY-031) и нагиба (KY-020) — „тампер” заштита од удара ветра, пада гране или обарања кућишта.',
          'DS18B20 дигитална сонда (1-Wire) — спољно мерење температуре тла/снега уз интерни BME688 сензор унутар кућишта.',
          'RGB LED (KY-016) — теренска дијагностика статуса при монтажи на дрво са аутоматским гашењем након 60 s.',
        ],
      },
      { type: 'h3', text: 'Шема повезивања (40-pin GPIO на Raspberry Pi 5)' },
      {
        type: 'code',
        lang: 'text',
        code: `        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power
GPIO 2  (Pin 3)│ ●  ● │(Pin 4)  5V Power
GPIO 3  (Pin 5)│ ●  ● │(Pin 6)  GND ─────────────► [GND] Заједничка маса свих сензора
GPIO 4  (Pin 7)│ ●  ● │(Pin 8)
   GND  (Pin 9)│ ●  ● │(Pin 10)
GPIO 17 (Pin 11)│ ●  ● │(Pin 12) GPIO 18
GPIO 27 (Pin 13)│ ●  ● │(Pin 14) GND
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [G] RGB LED Зелена (KY-016)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [B] RGB LED Плава  (KY-016)
               │ ●  ● │(Pin 20) GND
               └──────────────┘

  Детаљна веза сигнала:
  ├── BME688 клима/гас (I²C):
  │     ├── SDA ───────────────► GPIO 2 (Pin 3)
  │     ├── SCL ───────────────► GPIO 3 (Pin 5)
  │     ├── 3.3V ──────────────► Pin 1
  │     └── GND ───────────────► Pin 6
  │
  ├── IR Wake-up сензор (KY-032 / TCRT5000):
  │     ├── OUT (Digital) ─────► GPIO 17 (Pin 11)
  │     ├── VCC ───────────────► 3.3V (Pin 1 или Pin 17)
  │     └── GND ───────────────► GND
  │
  ├── Сензор ударца / вибрације (KY-002 / KY-031):
  │     ├── S (Сигнал) ────────► GPIO 27 (Pin 13)
  │     ├── VCC ───────────────► 3.3V
  │     └── GND ───────────────► GND
  │
  ├── DS18B20 температурна сонда (1-Wire):
  │     ├── DQ (Подаци) ───────► GPIO 4 (Pin 7) + 4.7kΩ pull-up отпорник на 3.3V
  │     ├── VDD ───────────────► 3.3V
  │     └── GND ───────────────► GND
  │
  └── RGB LED дијагностика (KY-016):
        ├── R (Црвена) ────────► GPIO 22 (Pin 15)
        ├── G (Зелена) ────────► GPIO 23 (Pin 16)
        ├── B (Плава)  ────────► GPIO 24 (Pin 18)
        └── - (GND)    ────────► GND (Pin 20)`,
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Уштеда батерије у шуми',
        text:
          'IR сензор троши мање од 15 mA. Коришћењем хардверског прекида, систем држи камеру и NPU у режиму спавања све док сноп није пресечен, чиме се аутономија на батерији продужава са неколико дана на више недеља.',
      },
      { type: 'h3', text: 'Пример кода за проширење (без мењања постојећег кода)' },
      {
        type: 'p',
        text: 'Ученици могу креирати класу у src/cuvar/hardware_upgrade.py:',
      },
      {
        type: 'code',
        lang: 'python',
        code: `"""Хардверски сензори из сета 37 у 1 за фотозамку Чувар Старе планине."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class FieldHardware:
    """Управља IR окидачем, сензором вибрације и дијагностичком LED диодом."""

    def __init__(
        self,
        pin_ir: int = 17,
        pin_shock: int = 27,
        pin_led_r: int = 22,
        pin_led_g: int = 23,
        pin_led_b: int = 24,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._ir = None
        self._shock = None
        self._led = None
        self.tamper_detected = False

        if not enabled:
            return

        try:
            from gpiozero import DigitalInputDevice, RGBLED

            self._ir = DigitalInputDevice(pin_ir, pull_up=False)
            self._shock = DigitalInputDevice(pin_shock, pull_up=True)
            self._led = RGBLED(red=pin_led_r, green=pin_led_g, blue=pin_led_b)

            self._shock.when_activated = self._on_tamper

            log.info("Теренски хардвер успешно покренут.")
            self.indicate_ready()
        except Exception as exc:
            log.warning("Теренски GPIO недоступан (%s) — рад без сензора из сета.", exc)
            self.enabled = False

    def _on_tamper(self) -> None:
        self.tamper_detected = True
        log.warning("ТАМПЕР АЛАРМ: Регистрован јак ударац или померање фотозамке!")

    def wait_for_motion(self, timeout_s: float = 10.0) -> bool:
        """Чека физички пролазак дивљачи испред IR сензора."""
        if not self.enabled or not self._ir:
            time.sleep(1)
            return True
        return self._ir.wait_for_active(timeout=timeout_s)

    def indicate_ready(self) -> None:
        """Кратка зелена индикација да је све спремно, па гашење светла."""
        if self._led:
            self._led.color = (0, 1, 0)
            time.sleep(2.0)
            self._led.off()

    def close(self) -> None:
        if self._led: self._led.close()
        if self._ir: self._ir.close()
        if self._shock: self._shock.close()`,
      },
      { type: 'h3', text: 'Брзи тест на плочи' },
      {
        type: 'code',
        lang: 'bash',
        code: `python -c "
from gpiozero import DigitalInputDevice, RGBLED; import time
led = RGBLED(22, 23, 24); ir = DigitalInputDevice(17)
print('Дијагностика: плава LED...'); led.color = (0, 0, 1); time.sleep(1)
print('Спремно: зелена LED...'); led.color = (0, 1, 0); time.sleep(1); led.off()
print('Пређи руком испред IR сензора (KY-032 / TCRT5000)...')
if ir.wait_for_active(timeout=5):
    print('Сноп пресечен! Окидање успешно.')
else:
    print('Време истекло (нема покрета).')
led.close(); ir.close()
"`,
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Галерија аутоматски снимљених кадрова са ознаком врсте.',
          'Графикон температуре, влажности и квалитета ваздуха.',
          'Процена трајања батерије на основу мерења из учионице.',
        ],
      },
    ],
  },

  {
    slug: 'kontrola-kvaliteta',
    broj: '04',
    naziv: 'Контрола квалитета без примера грешке',
    ikona: '🔬',
    kratko:
      'Визуелна контрола гумених и текстилних узорака кроз детекцију аномалија — модел се тренира само на исправним комадима.',
    status: 'предлог',
    boja: '#E5B842',
    cvor: 'Контрола квалитета',
    pozicija: [3.2, -1.34, 0.99],
    hardver: ['Raspberry Pi 5', 'AI HAT+ Hailo-8L', 'Camera Module 3', 'Сет 37 у 1'],
    tehnologije: ['PatchCore / PaDiM', 'контролисано осветљење', 'GPIO актуација'],
    uputstvo: 'ai-hat-hailo',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/kontrola-kvaliteta',
    telemetrija: {
      latencija: '45 ms / узорку',
      npuCpu: 'Hailo-8L NPU',
      potrosnja: '~5.5 W',
      offline: '100% Офлајн',
      fps: '22 FPS',
      model: 'PatchCore аномалије',
    },
    pipeline: [
      { icon: '📷', title: 'Индустријска камера', detail: 'Контролисано дифузно светло узорка' },
      { icon: '⚡', title: 'Hailo-8L екстрактор', detail: 'Извлачење карактеристика структуре' },
      { icon: '🎯', title: 'PatchCore модул', detail: 'Поређење само са исправним комадима' },
      { icon: '🔥', title: 'Топлотна мапа грешке', detail: 'Лоцирање мане на гуми/тканини' },
      { icon: '🚨', title: 'Селектор / Аларм', detail: 'Издвајање комада са маном са траке' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Камера гледа узорак на траци. Модел је видео само исправне комаде и пријављује све што одступа — рупу, ману у ткању, страно тело.',
      },
      { type: 'h', text: 'Зашто детекција аномалија, а не класификација' },
      {
        type: 'ul',
        items: [
          'Шкартова никад нема довољно за тренинг класификатора — исправних комада има колико хоћеш.',
          'То је приступ који се стварно користи у индустрији.',
          'Ученици уче да раде са неуравнотеженим подацима.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Природна веза са пиротском привредом',
        text:
          'Гумарска и текстилна производња у Пироту — повод за писмо о сарадњи и реалне узорке за рад.',
      },
      { type: 'h', text: 'Радно место' },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Поставка изнад траке',
        caption:
          'Камера гледа право надоле, а светло долази са стране кроз дифузор. Осветљење мора да буде исто на сваком комаду — иначе модел пријави сенку као ману.',
        data: {
          kamera: { naziv: 'Камера изнад траке', vfov: 46, visina: '≈ 40 cm' },
          zone: [
            { naziv: 'Поље снимања', od: 30, do: 72 },
          ],
          objekti: [
            { ikona: '💡', naziv: 'Дифузор', x: 18, y: 50 },
            { ikona: '🟩', naziv: 'Узорак', x: 50, y: 52 },
            { ikona: '💡', naziv: 'Дифузор', x: 82, y: 50 },
          ],
          tlo: 'Трака са узорцима — поглед одозго',
        },
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Исти склоп као код „Паметне зебре“ — разлика је у моделу и у осветљењу, не у хардверу.',
        data: {
          ploca: 'Raspberry Pi 5',
          veze: [
            { port: 'PCIe', ikona: '⚡', naziv: 'AI HAT+ (Hailo-8L)', detalj: 'извлачење карактеристика' },
            { port: 'CSI', ikona: '📷', naziv: 'Camera Module 3', detalj: 'фиксни фокус изнад траке' },
            { port: 'GPIO', ikona: '🚨', naziv: 'Селектор & Andon стуб', detalj: 'Релеј за шкарт, зујалица и енкодер' },
            { port: '5 V', ikona: '💡', naziv: 'LED осветљење', detalj: 'дифузно, стално исто' },
          ],
        },
      },
      { type: 'h', text: 'Хардверска надградња (Сет 37 у 1)' },
      {
        type: 'p',
        text:
          'У индустријском инспекцијском столу систем се надграђује периферијама из сета 37 у 1 ради потпуне аутоматизације синхронизације са траком и избацивања шкарта:',
      },
      {
        type: 'steps',
        items: [
          'Оптички прекидач са прорезом (KY-010 / TCRT5000) на GPIO 17 — синхронизовани окидач: снима кадар тачно када комад стигне на позицију за снимање.',
          '5V Релеј (KY-019) на GPIO 27 — пнеуматски селектор: физички избацује узорак са траке чим PatchCore детектује ману.',
          'Andon LED сигнализација (KY-016 / KY-011) на GPIO 25 (црвена) и 26 (зелена) — фабрички светлосни статус: OK / Defect.',
          'Активна зујалица (KY-012) на GPIO 22 — звучно обавештење оператера о одбаченом шкарт комаду.',
          'Ротациони енкодер (KY-040) на GPIO 18, 23, 24 — хардверско подешавање прага осетљивости и тастер за рекалибрацију у ходу.',
        ],
      },
      { type: 'h3', text: 'Шема повезивања (40-pin GPIO на Raspberry Pi 5)' },
      {
        type: 'code',
        lang: 'text',
        code: `        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power ────────► [VCC] 5V Релеј (KY-019)
               │ ●  ● │(Pin 4)  5V Power
   GND  (Pin 6)│ ●  ● │(Pin 5)
               │ ●  ● │(Pin 9)  GND ─────────────► [GND] Заједничка маса свих модула
GPIO 17 (Pin 11)│ ●  ● │(Pin 12) GPIO 18 ────────► [CLK] Ротациони енкодер (KY-040)
GPIO 27 (Pin 13)│ ●  ● │(Pin 14) GND
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [DT]  Ротациони енкодер (KY-040)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [SW]  Енкодер тастер    (KY-040)
               │ ●  ● │(Pin 20) GND
GPIO 25 (Pin 22)│ ●  ● │(Pin 21)
               └──────────────┘

  Детаљна веза сигнала:
  ├── Оптички окидач камере (KY-010 / TCRT5000):
  │     ├── OUT (Digital) ─────► GPIO 17 (Pin 11)
  │     ├── VCC ───────────────► 3.3V (Pin 1)
  │     └── GND ───────────────► GND (Pin 6 или 9)
  │
  ├── 5V Релеј за избацивање шкарта (KY-019):
  │     ├── IN ────────────────► GPIO 27 (Pin 13)
  │     ├── VCC ───────────────► 5V  (Pin 2)
  │     └── GND ───────────────► GND
  │
  ├── Активна зујалица (KY-012):
  │     ├── S (Сигнал) ────────► GPIO 22 (Pin 15)
  │     └── - (GND)    ────────► GND
  │
  ├── Двобојна / RGB LED Andon индикација:
  │     ├── R (Црвена) ────────► GPIO 25 (Pin 22)
  │     ├── G (Зелена) ────────► GPIO 26 (Pin 37)
  │     └── GND ───────────────► GND (Pin 20)
  │
  └── Ротациони енкодер за праг (KY-040):
        ├── CLK ───────────────► GPIO 18 (Pin 12)
        ├── DT  ───────────────► GPIO 23 (Pin 16)
        ├── SW (Тастер) ───────► GPIO 24 (Pin 18)
        ├── VCC ───────────────► 3.3V
        └── GND ───────────────► GND`,
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Индустријски Andon стандард и безбедност напајања',
        text:
          'Ученици уче како се софтверски излаз детекције аномалија директно преводи у стандардне фабричке сигнале — светлосни стуб, звучни аларм и пнеуматско сортирање. Напомена: Релеј се напаја са 5V због шпулне, док су контролни сигнали строго на 3.3V логици Raspberry Pi 5 плоче.',
      },
      { type: 'h3', text: 'Пример кода за проширење (без мењања постојећег кода)' },
      {
        type: 'p',
        text: 'Ученици могу креирати класу у src/qc/hardware_upgrade.py:',
      },
      {
        type: 'code',
        lang: 'python',
        code: `"""Индустријска хардверска периферија из сета 37 у 1 за контролу квалитета."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class QualityControlHardware:
    """Управља оптичким окидачем, релејем за шкарт, Andon LED-ом и зујалицом."""

    def __init__(
        self,
        pin_trigger: int = 17,
        pin_relay: int = 27,
        pin_buzzer: int = 22,
        pin_led_ok: int = 26,
        pin_led_defect: int = 25,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._trigger = None
        self._relay = None
        self._buzzer = None
        self._led_ok = None
        self._led_defect = None

        if not enabled:
            return

        try:
            from gpiozero import DigitalInputDevice, OutputDevice, Buzzer, LED

            self._trigger = DigitalInputDevice(pin_trigger, pull_up=False)
            self._relay = OutputDevice(pin_relay, active_high=True, initial_value=False)
            self._buzzer = Buzzer(pin_buzzer)
            self._led_ok = LED(pin_led_ok)
            self._led_defect = LED(pin_led_defect)

            log.info("Индустријски контролер 37 у 1 иницијализован.")
            self.set_idle()
        except Exception as exc:
            log.warning("GPIO недоступан (%s) — софтверски симулатор.", exc)
            self.enabled = False

    def wait_for_part(self, timeout_s: float = 5.0) -> bool:
        """Чека да оптички сноп региструје узорак на позицији за снимање."""
        if not self.enabled or not self._trigger:
            time.sleep(0.5)
            return True
        return self._trigger.wait_for_active(timeout=timeout_s)

    def report_result(self, is_defect: bool) -> None:
        """Пријављује резултат инспекције на Andon индикаторима и релеју."""
        if not self.enabled:
            return

        if is_defect:
            if self._led_ok: self._led_ok.off()
            if self._led_defect: self._led_defect.on()
            if self._buzzer: self._buzzer.beep(on_time=0.1, off_time=0.1, n=2)
            # Активирање избацивача шкарта на 300 ms
            if self._relay:
                self._relay.on()
                time.sleep(0.3)
                self._relay.off()
            log.warning("ШКАРТ ОДБАЧЕН: Активиран пнеуматски релеј!")
        else:
            if self._led_defect: self._led_defect.off()
            if self._led_ok: self._led_ok.on()
            if self._buzzer: self._buzzer.off()

    def set_idle(self) -> None:
        if self._led_ok: self._led_ok.on()
        if self._led_defect: self._led_defect.off()
        if self._buzzer: self._buzzer.off()
        if self._relay: self._relay.off()

    def close(self) -> None:
        for dev in (self._trigger, self._relay, self._buzzer, self._led_ok, self._led_defect):
            if dev: dev.close()`,
      },
      { type: 'h3', text: 'Брзи тест на плочи' },
      {
        type: 'code',
        lang: 'bash',
        code: `python -c "
from gpiozero import OutputDevice, Buzzer, LED; import time
relay = OutputDevice(27); buzz = Buzzer(22); led_ok = LED(26); led_bad = LED(25)
print('Тест: Исправан комад (OK)...'); led_ok.on(); time.sleep(1); led_ok.off()
print('Тест: Дефект (Шкарт) + релеј...'); led_bad.on(); buzz.beep(0.1, 0.1, 2); relay.on(); time.sleep(0.3); relay.off()
led_bad.off(); relay.close(); buzz.close(); led_ok.close(); led_bad.close()
"`,
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Уживо приказ: исправан комад — тишина, комад са маном — аларм и топлотна мапа одступања.',
          'Табела тачности на тест узорцима.',
        ],
      },
    ],
  },

  {
    slug: 'znakovna-azbuka',
    broj: '05',
    naziv: 'Знаковна азбука',
    ikona: '🖐️',
    kratko:
      'Препознавање слова српске знаковне азбуке преко тачака шаке и временског класификатора покрета.',
    status: 'предлог',
    boja: '#60A5FA',
    cvor: 'Знаковна азбука',
    pozicija: [3.01, 0.59, -0.93],
    hardver: ['Raspberry Pi 5', 'AI Camera IMX500', 'Сет 37 у 1'],
    tehnologije: ['детекција тачака шаке', 'сопствени скуп података', 'Label Studio', 'GPIO фидбек'],
    uputstvo: 'ai-camera-imx500',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/znakovna-azbuka',
    telemetrija: {
      latencija: '35 ms',
      npuCpu: 'IMX500 / Pi 5 CPU',
      potrosnja: '~4.9 W',
      offline: '100% Офлајн',
      fps: '25 FPS',
      model: 'MediaPipe 21-point + MLP',
    },
    pipeline: [
      { icon: '📷', title: 'AI Камера', detail: 'Снимање гестова руке у учионици' },
      { icon: '🖐️', title: 'Детектор шаке', detail: 'Праћење 21 тачке зглобова прстију' },
      { icon: '📐', title: 'Нормализација', detail: 'Инваријантност на угао и удаљеност' },
      { icon: '🧠', title: 'MLP Класификатор', detail: 'Препознавање слова знаковне азбуке' },
      { icon: '🖥️', title: 'Текст / Говор', detail: 'Испиши слово и симулирај изговор' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Камера прати шаку, модел из положаја прстију препознаје слово знаковне азбуке и исписује га на екрану.',
      },
      { type: 'h', text: 'Зашто остаје из пријаве' },
      {
        type: 'p',
        text:
          'Носи тему инклузије и најбољи је увод у рад са сопственим подацима: ученици сами снимају и анотирају скуп слика у Label Studio-у — тачно оно што активност „развој курикулума и модела“ описује.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'Детектор тачака шаке даје 21 тачку по кадру.',
          'Тачке се нормализују (положај, величина, ротација шаке).',
          'Мали класификатор препознаје статична слова; за слова са покретом користи се низ кадрова.',
          'Ученици проширују скуп података новим сниманцима и поново тренирају.',
        ],
      },
      {
        type: 'shema',
        kind: 'tackeShake',
        naslov: 'Шта модел заправо види',
        caption:
          'Класификатор не добија слику руке него 21 координату. Зато препознавање не зависи од боје коже, рукава ни позадине — а скуп података остаје мали.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Најједноставнији склоп у програму — камера и екран. Cела обрада стаје на плочу, без акцелератора.',
        data: {
          ploca: 'Raspberry Pi 5',
          veze: [
            { port: 'CSI', ikona: '📷', naziv: 'AI Camera IMX500', detalj: 'шака у кадру, 25 FPS' },
            { port: 'HDMI', ikona: '🖥️', naziv: 'Екран са словом', detalj: 'испис препознатог слова' },
            { port: 'GPIO', ikona: '🖐️', naziv: 'Тастер & LED фидбек', detalj: 'Окидач узорака и звучни одзив' },
            { port: 'USB-C', ikona: '🔌', naziv: 'Напајање 27 W', detalj: 'стандардно за Pi 5' },
          ],
        },
      },
      { type: 'h', text: 'Хардверска надградња (Сет 37 у 1)' },
      {
        type: 'p',
        text:
          'За интерактивни рад са ученицима и инклузивне радионице, систем се обогаћује тактилном и визуелном периферијом из сета 37 у 1:',
      },
      {
        type: 'steps',
        items: [
          'Тактилни тастер (KY-004) на GPIO 16 — физички окидач: снима узорак без гледања и куцања по тастатури, чим ученик формира исправан знак шаком.',
          'RGB LED (KY-016) на GPIO 17, 27, 22 — инстант фидбек: жуто док се проверава положај, зелено за потврђено слово, црвено за непрепознат знак.',
          'Пасивна зујалица (KY-006) на GPIO 25 — мелодијски тон одређене висине за свако потврђено слово (мултисензорно учење).',
          'Ротациони енкодер (KY-040) на GPIO 18, 23, 24 — физички бирач слова азбуке за тренинг директно са кутије уређаја.',
        ],
      },
      { type: 'h3', text: 'Шема повезивања (40-pin GPIO на Raspberry Pi 5)' },
      {
        type: 'code',
        lang: 'text',
        code: `        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power
               │ ●  ● │(Pin 6)  GND ─────────────► [GND] Заједничка маса
GPIO 17 (Pin 11)│ ●  ● │(Pin 12) GPIO 18 ────────► [CLK] Енкодер бирач (KY-040)
GPIO 27 (Pin 13)│ ●  ● │(Pin 16) GPIO 23 ────────► [DT]  Енкодер бирач (KY-040)
GPIO 22 (Pin 15)│ ●  ● │(Pin 18) GPIO 24 ────────► [SW]  Енкодер тастер (KY-040)
               │ ●  ● │(Pin 22) GPIO 25 ────────► [S]   Пасивна зујалица (KY-006)
GPIO 26 (Pin 37)│ ●  ● │(Pin 36) GPIO 16 ────────► [S]   Тастер за узорке (KY-004)
               └──────────────┘

  Детаљна веза сигнала:
  ├── Тастер за снимање узорка (KY-004):
  │     ├── S (Сигнал) ────────► GPIO 16 (Pin 36)
  │     ├── VCC ───────────────► 3.3V (Pin 1)
  │     └── GND ───────────────► GND (Pin 6 или 14)
  │
  ├── RGB LED визуелни фидбек (KY-016):
  │     ├── R (Црвена) ────────► GPIO 17 (Pin 11)
  │     ├── G (Зелена) ────────► GPIO 27 (Pin 13)
  │     ├── B (Плава)  ────────► GPIO 22 (Pin 15)
  │     └── - (GND)    ────────► GND
  │
  ├── Пасивна зујалица за тонове (KY-006):
  │     ├── S (Сигнал PWM) ────► GPIO 25 (Pin 22)
  │     └── - (GND)    ────────► GND
  │
  └── Ротациони енкодер (KY-040):
        ├── CLK ───────────────► GPIO 18 (Pin 12)
        ├── DT  ───────────────► GPIO 23 (Pin 16)
        ├── SW (Потврда) ──────► GPIO 24 (Pin 18)
        ├── VCC ───────────────► 3.3V
        └── GND ───────────────► GND`,
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Педагошка вредност и инклузивни дизајн',
        text:
          'Физички тастер омогућава ученицима да самостално прикупе десетине квалитетних узорака за неколико минута, док звучни и светлосни одзив чине апликацију доступном за учење деци свих узраста без потребе за гледањем у терминал.',
      },
      { type: 'h3', text: 'Пример кода за проширење (без мењања постојећег кода)' },
      {
        type: 'p',
        text: 'Ученици могу креирати класу у src/znak/hardware_upgrade.py:',
      },
      {
        type: 'code',
        lang: 'python',
        code: `"""Хардверски фидбек из сета 37 у 1 за Знаковну азбуку."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class SignLanguageFeedback:
    """Управља тастером за снимање, RGB статусом и звучним фидбеком."""

    def __init__(
        self,
        pin_btn: int = 16,
        pin_r: int = 17,
        pin_g: int = 27,
        pin_b: int = 22,
        pin_buzzer: int = 25,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._btn = None
        self._led = None
        self._buzzer = None

        if not enabled:
            return

        try:
            from gpiozero import Button, RGBLED, TonalBuzzer

            self._btn = Button(pin_btn, pull_up=True)
            self._led = RGBLED(red=pin_r, green=pin_g, blue=pin_b)
            self._buzzer = TonalBuzzer(pin_buzzer)

            log.info("Хардвер за знаковну азбуку иницијализован.")
            self.set_waiting()
        except Exception as exc:
            log.warning("GPIO недоступан (%s) — софтверски режим.", exc)
            self.enabled = False

    def is_record_pressed(self) -> bool:
        """Враћа True ако ученик притиска физички тастер за унос узорка."""
        return bool(self._btn and self._btn.is_pressed)

    def set_waiting(self) -> None:
        if self._led: self._led.color = (0.2, 0.2, 0)  # Блага жута

    def set_recognized(self, note: str = "C5") -> None:
        """Потврда: зелено светло + кратак мелодијски тон."""
        if not self.enabled: return
        if self._led: self._led.color = (0, 1, 0)
        if self._buzzer:
            try:
                self._buzzer.play(note)
                time.sleep(0.12)
                self._buzzer.stop()
            except Exception:
                pass

    def set_unknown(self) -> None:
        if self._led: self._led.color = (1, 0, 0)  # Црвено

    def close(self) -> None:
        for dev in (self._btn, self._led, self._buzzer):
            if dev: dev.close()`,
      },
      { type: 'h3', text: 'Брзи тест на плочи' },
      {
        type: 'code',
        lang: 'bash',
        code: `python -c "
from gpiozero import Button, RGBLED; import time
btn = Button(16); led = RGBLED(17, 27, 22)
print('Држи руку у кадру. Притисни тастер (KY-004) на GPIO 16 за снимање...')
led.color = (1, 1, 0)
btn.wait_for_press(timeout=5)
print('Тастер притиснут! Узорак снимљен.')
led.color = (0, 1, 0); time.sleep(1); led.off()
btn.close(); led.close()
"`,
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Посетилац показује слово, уређај га исписује.',
          'Приказ како тачност расте са величином скупа података.',
        ],
      },
    ],
  },

  {
    slug: 'skolski-asistent',
    broj: '06',
    naziv: 'Школски асистент',
    ikona: '🧑‍🏫',
    kratko:
      'Упериш камеру на радни лист, шему или инструмент и питаш на српском — одговор се рачуна локално, на уређају, без облака.',
    status: 'предлог',
    boja: '#4ED8A3',
    cvor: 'Школски асистент',
    pozicija: [1.99, 1.36, 1.42],
    hardver: ['Jetson Orin Nano (8 GB)', 'Logitech C922', 'активни хладњак', 'NVMe SSD'],
    tehnologije: ['Qwen2-VL (VLM)', 'faster-whisper', 'Piper TTS', 'RAG над материјалима'],
    uputstvo: 'skolski-asistent-postavka',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/skolski-asistent',
    telemetrija: {
      latencija: '~2.5 s до одговора',
      npuCpu: 'Orin Nano 8 GB (до 67 TOPS)',
      potrosnja: '~15 W',
      offline: '100% Офлајн',
      memorija: '~6 GB VRAM',
      model: 'Qwen2-VL 2B (int4)',
    },
    pipeline: [
      { icon: '📷', title: 'C922 камера', detail: 'Радни лист или шема, 1080p, аутофокус' },
      { icon: '🎙️', title: 'Whisper int8', detail: 'Питање на српском → текст, локално' },
      { icon: '🖼️', title: 'VLM Qwen2-VL', detail: 'Спаја слику и питање, рачуна на Orin-у' },
      { icon: '📚', title: 'RAG над градивом', detail: 'Довлачење из школских приручника (опционо)' },
      { icon: '🔊', title: 'Piper TTS', detail: 'Одговор изговорен на српском и исписан' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Ученик упери камеру на задатак, шему везивања или мерни инструмент и питање постави гласом, на српском. Модел који „види и чита“ ради на самом уређају и врати одговор — говором и текстом. Иста ствар коју нуде велики онлајн сервиси, овде без слања слике и гласа било коме.',
      },
      { type: 'h', text: 'Зашто баш јачи уређај' },
      {
        type: 'p',
        text:
          'Осталих пет пројеката ради на Raspberry Pi-ју са малим моделима за једну ствар. Овде треба језички модел који истовремено гледа слику и разуме питање — то на Pi-ју не иде. Jetson Orin Nano (8 GB) покреће квантизован VLM од 2 милијарде параметара уживо; уз JetPack 6.2 иста плоча ради у „Super“ режиму (до 67 TOPS). То је прилика да ученици виде докле „мало“ рачунарство данас стиже.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'Камера ухвати кадар (радни лист, електрична шема, отпорник, дисплеј инструмента).',
          'Whisper (int8) претвара изговорено питање у текст — све локално.',
          'VLM (Qwen2-VL, int4) добија слику и питање и формулише одговор на српском.',
          'Опционо: пре одговора се из локалне базе школских материјала довуку релевантни пасуси (RAG), па модел одговара с ослонцем на градиво.',
          'Piper синтетише говор на српском; одговор се и исписује на екрану.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Ништа не напушта учионицу',
        text:
          'Модели се преузму једном. После тога нема мреже — ни слика, ни глас, ни питања не одлазе на туђи сервер.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'NVIDIA Jetson Orin Nano Developer Kit (8 GB)',
          'Logitech C922 Pro Stream (1080p, аутофокус, стерео микрофон)',
          'Активни хладњак и напајање 19 V',
          'NVMe SSD за моделе и базу материјала',
          'Звучник или слушалице за изговорени одговор',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Једини уређај у програму који не носи Raspberry Pi. Модели живе на NVMe диску, не на картици — картица би овде била уско грло.',
        data: {
          ploca: 'Jetson Orin Nano (8 GB)',
          veze: [
            { port: 'USB 3', ikona: '🎥', naziv: 'Logitech C922', detalj: '1080p + стерео микрофон' },
            { port: 'M.2', ikona: '💽', naziv: 'NVMe SSD', detalj: 'модели и база материјала' },
            { port: '3.5 mm', ikona: '🔊', naziv: 'Звучник', detalj: 'изговорен одговор (Piper)' },
            { port: 'DP', ikona: '🖥️', naziv: 'Екран', detalj: 'исписан одговор уз говор' },
            { port: '19 V', ikona: '🔌', naziv: 'Напајање и хладњак', detalj: 'Super режим тражи хлађење' },
          ],
        },
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Обазриво са тачношћу',
        text:
          'Мали VLM понекад погреши. Пројекат учи и томе: одговор се проверава, RAG му даје ослонац у уџбенику, а на Demo Day-у се мери колико пута погоди.',
      },
      { type: 'h', text: 'Наставна вредност' },
      {
        type: 'ul',
        items: [
          'Квантизација — зашто int4 модел стаје у 8 GB и колико изгуби на тачности.',
          'VLM и мултимодалност — како се слика и текст спајају у један одговор.',
          'RAG — довлачење из сопствене базе знања уместо „измишљања“.',
          'Мерење латенције и потрошње — цена сваког корака у ланцу.',
        ],
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Посетилац покаже шему или задатак и постави питање — уређај одговори наглас.',
          'Пребацивач: са и без RAG-а над школским приручником.',
          'Табела тачности и график кашњења по кораку ланца.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Помоћ у учионици и на пракси која ради и кад нема интернета — за допунску наставу, рад код куће без претплате и ученике којима треба објашњење још једном, својим темпом.',
      },
    ],
  },

  {
    slug: 'djak-za-volanom',
    broj: '07',
    naziv: 'Ђак за воланом',
    ikona: '🏎️',
    kratko:
      'Ауто у размери 1:10 сам вози по стази — камера држи траку, а RPLIDAR је независни сигурносни слој који кочи на препреку.',
    status: 'предлог',
    boja: '#E5B842',
    cvor: 'Ђак за воланом',
    pozicija: [1.55, -2.11, -2.28],
    hardver: ['PiRacer AI Kit', 'Raspberry Pi 4', 'RPLIDAR A1', 'камера напред'],
    tehnologije: ['CNN behavioral cloning', 'TensorFlow Lite', 'фузија сензора', 'PWM управљање'],
    uputstvo: 'djak-za-volanom-postavka',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/djak-za-volanom',
    telemetrija: {
      latencija: '~35 ms / одлуци',
      npuCpu: 'Raspberry Pi 4 (TFLite int8)',
      potrosnja: '~6 W + мотори',
      offline: '100% Офлајн',
      fps: '20 одлука/с',
      model: 'CNN 120×160 (behavioral cloning)',
    },
    pipeline: [
      { icon: '📷', title: 'Камера напред', detail: 'Слика стазе 120×160, 20+ FPS' },
      { icon: '🧠', title: 'CNN политика', detail: 'Из слике предвиђа угао волана и гас' },
      { icon: '🌀', title: 'RPLIDAR 360°', detail: 'Најближа препрека у сектору испред аута' },
      { icon: '🛡️', title: 'Сигурносни арбитар', detail: 'Лидар прекида CNN и кочи на препреку' },
      { icon: '🚗', title: 'PWM → серво + ESC', detail: 'Волан и гас на стварну стазу' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Ученици направе стазу селотејп тракама на поду, провозају ауто ручно и сниме своје вожње. Мали CNN научи из тих снимака да предвиди угао волана из слике. Онда ауто вози сам, а RPLIDAR цело време независно скенира 360° и зауставља га пред препреком — без обзира на то шта камера „мисли“.',
      },
      { type: 'h', text: 'Зашто камера И лидар' },
      {
        type: 'p',
        text:
          'Камерски модел је научен на стази какву је видео — на новом осветљењу или пред препреком коју није срео, погреши. Зато одлуку о кочењу не доноси он него засебан, једноставан систем над лидаром. То је основни принцип безбедних аутономних система: критична функција не сме да зависи од једног модела.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'Снимање: ученик вози ауто гејмпадом, систем чува слику камере + командни угао/гас (десетине минута вожње).',
          'Обука: мали CNN (улаз 120×160) учи да из слике предвиди угао волана; тренинг на рачунару, извоз у TensorFlow Lite.',
          'Аутономна вожња: модел на Pi-ју даје угао 20 пута у секунди; PWD драјвер (PCA9685) окреће серво и задаје гас.',
          'Сигурносни слој: из RPLIDAR скена рачуна се најмање растојање у конусу испред аута; испод прага — гас на нулу, кочница.',
          'Итерација: погледа се где ауто излети са стазе, ту се сними још података, модел се поново обучи.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Сигурносни слој не учи',
        text:
          'Арбитар над лидаром је обичан праг на растојању, не неуронска мрежа. Може се објаснити, тестирати и не мења се тренингом — зато му се верује да заустави ауто.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'Waveshare PiRacer AI Kit (шасија 1:10, серво, ESC, PCA9685, INA219, OLED)',
          'Raspberry Pi 4 (4 GB) са активним хлађењем',
          'Камера са широким углом, монтирана напред',
          'Slamtec RPLIDAR A1 (360°, до 12 m) на USB',
          'Пакет 2× 18650 за вожњу + power bank за Pi (по потреби)',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Обрати пажњу на две одвојене гране: камера иде у модел, лидар иде у сигурносни арбитар. Оне се састају тек на PCA9685 — тамо арбитар има последњу реч.',
        data: {
          ploca: 'Raspberry Pi 4 (4 GB)',
          veze: [
            { port: 'CSI', ikona: '📷', naziv: 'Камера напред', detalj: 'широки угао, улаз 120×160' },
            { port: 'USB', ikona: '🌀', naziv: 'RPLIDAR A1', detalj: '360°, до 12 m — засебна грана' },
            { port: 'I²C', ikona: '🎛️', naziv: 'PCA9685 (PWM)', detalj: 'серво волана и ESC гаса' },
            { port: 'I²C', ikona: '🔋', naziv: 'INA219 + OLED', detalj: 'струја пакета и статус' },
            { port: 'USB', ikona: '🎮', naziv: 'Гејмпад', detalj: 'само при снимању података' },
          ],
        },
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Сигурносни конус лидара',
        caption:
          'Арбитар не гледа цео круг од 360° него само конус испред аута. У њему тражи најмање растојање; испод прага гас пада на нулу — без питања модела.',
        data: {
          kamera: { naziv: 'RPLIDAR на крову аута', vfov: 60, visina: '360°' },
          zone: [
            { naziv: 'Кочница — испод прага', od: 6, do: 34 },
            { naziv: 'Опрез — успори', od: 40, do: 74 },
          ],
          objekti: [
            { ikona: '📦', naziv: 'Препрека', x: 46, y: 26 },
            { ikona: '🧱', naziv: 'Ивица стазе', x: 84, y: 56 },
          ],
          tlo: 'Стаза у учионици — поглед одозго',
        },
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Прво споро, па брже',
        text:
          'На пуном гасу и модел и лидар касне превише. Ограничи брзину док не буде поуздано; тек онда подижи. Стаза са благим кривинама, без оштрих углова на почетку.',
      },
      { type: 'h', text: 'Наставна вредност' },
      {
        type: 'ul',
        items: [
          'Цео ML циклус на једном пројекту: подаци → обука → примена → анализа грешака → још података.',
          'Behavioral cloning — учење из демонстрације, и његова главна слабост (не зна шта не зна).',
          'Фузија сензора и архитектура безбедности: зашто критична одлука не иде кроз модел.',
          'Реално време: буџет од 50 ms по кадру, шта стаје у њега.',
        ],
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Ауто круж­и стазом сам; посетилац стави препреку — ауто стане.',
          'Екран уживо: слика камере са предвиђеним волан, поред ње лидар скен са сектором опасности.',
          'Кратак снимак „вожња 1 vs вожња 20“ — колико података треба да престане да излеће.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Пар са пројектом „Паметна зебра“: тамо се пешачки прелаз посматра одозго, овде из аутомобила. Иста ситуација, два угла — основа за разговор о безбедности саобраћаја код школе.',
      },
    ],
  },

  {
    slug: 'hodnik-u-glavi',
    broj: '08',
    naziv: 'Ходник у глави',
    ikona: '🗺️',
    kratko:
      'Возило с једним ласерским сензором провоза ходник, у ходу нацрта 2D мапу и онда само нађе пут до задате тачке.',
    status: 'предлог',
    boja: '#5FBA98',
    cvor: 'Ходник у глави',
    pozicija: [1.23, -0.18, 2.23],
    hardver: ['RPLIDAR A1', 'PiRacer шасија', 'Raspberry Pi 4'],
    tehnologije: ['scan-matching SLAM (ICP)', 'occupancy grid', 'A* планирање', 'pure pursuit'],
    uputstvo: 'hodnik-u-glavi-slam',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/hodnik-u-glavi',
    telemetrija: {
      latencija: '~180 ms / скену',
      npuCpu: 'Raspberry Pi 4 (NumPy)',
      potrosnja: '~5 W',
      offline: '100% Офлајн',
      senzor: 'RPLIDAR A1, 5.5 Hz',
      mapa: 'grid 5 cm, log-odds',
    },
    pipeline: [
      { icon: '🌀', title: 'RPLIDAR скен', detail: '360° тачака, ~5 пута у секунди' },
      { icon: '📐', title: 'ICP поравнање', detail: 'Нови скен на постојећу мапу → помак возила' },
      { icon: '🗺️', title: 'Occupancy grid', detail: 'Зракови уписују слободно/зузето (log-odds)' },
      { icon: '🧭', title: 'A* планер', detail: 'Најкраћи пут кроз слободне ћелије до циља' },
      { icon: '🚗', title: 'Pure pursuit', detail: 'Волан и брзина да возило прати пут' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Возило нема GPS ни план школе. Има само један ласерски сензор који мери растојање до зидова у круг. Док га ученици провозају (или гурну) кроз ходник, оно поравнава сваки нови скен на оно што је већ видело, из тог поравнања рачуна колико се померило и попуњава 2D мапу. Кад мапа постоји, задаш тачку — возило само нађе пут и оде тамо.',
      },
      { type: 'h', text: 'Зашто без одометрије' },
      {
        type: 'p',
        text:
          'PiRacer нема сензоре на точковима, па се помак не мери из погона него из самих скенова — алгоритмом ICP (iterative closest point), који два облака тачака „склопи“ један на други. То је срж класичног SLAM-а и ради без иједног додатног сензора; цена је што возило мора да иде споро.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'Скен из поларних координата (угао, растојање) претвара се у тачке у равни.',
          'ICP поравнава нови скен на мапу и даје померај и заокрет од претходног положаја.',
          'Из новог положаја се за сваки зрак Брезенхамовом линијом уписује: пут до тачке = слободно, тачка = зузето (log-odds, отпорно на шум).',
          'A* тражи најкраћи низ слободних ћелија од возила до циља; препреке се прошире за ширину возила.',
          'Pure pursuit бира тачку на путу испред возила и рачуна угао волана да је стигне.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Све су класични алгоритми',
        text:
          'ICP, occupancy grid, A*, pure pursuit — ниједан није неуронска мрежа. Свaки стаје у педесетак линија и има тест. Ученици виде математику, не црну кутију.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'Slamtec RPLIDAR A1 (360°, до 12 m, 5.5 Hz) на USB',
          'PiRacer шасија са пројекта „Ђак за воланом“ (или колица за гурање)',
          'Raspberry Pi 4 (4 GB) + активно хлађење',
          'Раван под и ходник са зидовима — RPLIDAR не види стакло',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Најкраћа шема у програму: један сензор и један погон. Све остало је математика на процесору — нема акцелератора, нема камере.',
        data: {
          ploca: 'Raspberry Pi 4 (4 GB)',
          veze: [
            { port: 'USB', ikona: '🌀', naziv: 'RPLIDAR A1', detalj: '360°, 5,5 Hz, до 12 m' },
            { port: 'I²C', ikona: '🎛️', naziv: 'PCA9685 → погон', detalj: 'серво и ESC PiRacer шасије' },
            { port: 'HDMI', ikona: '🗺️', naziv: 'Екран са мапом', detalj: 'мапа расте уживо' },
            { port: 'USB-C', ikona: '🔋', naziv: 'Power bank', detalj: 'напајање плоче у вожњи' },
          ],
        },
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Шта лидар види у ходнику',
        caption:
          'Лидар мери растојање у све стране и добија обрис зидова. Стакло и огледала у том обрису недостају — зато се мапира ходник са зидовима, не улаз са стакленим вратима.',
        data: {
          kamera: { naziv: 'RPLIDAR на возилу', vfov: 120, visina: '360°' },
          zone: [
            { naziv: 'Слободне ћелије — прођи', od: 10, do: 58 },
            { naziv: 'Заузето — зид', od: 64, do: 82 },
          ],
          objekti: [
            { ikona: '🧱', naziv: 'Зид лево', x: 12, y: 44 },
            { ikona: '🧱', naziv: 'Зид десно', x: 88, y: 44 },
            { ikona: '🚪', naziv: 'Циљ', x: 50, y: 74 },
          ],
          tlo: 'Школски ходник — поглед одозго',
        },
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Спор сензор, спора вожња',
        text:
          'RPLIDAR A1 се врти 5–6 пута у секунди. Ако возило јури, скенови се „размажу“ и ICP омане. Прво гурање руком, па спора аутономна вожња.',
      },
      { type: 'h', text: 'Наставна вредност' },
      {
        type: 'ul',
        items: [
          'SLAM без мистике: одакле возило „зна“ где је кад нема GPS.',
          'ICP — поравнање облака тачака, конвергенција и када омане.',
          'Репрезентација простора: зашто log-odds мрежа а не листа зидова.',
          'Планирање пута (A*) и праћење пута (pure pursuit) — две одвојене ствари.',
        ],
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Уживо: возило се провезе делом сале, мапа расте на екрану.',
          'Посетилац кликне тачку на мапи — возило оде тамо, заобилазећи препреке.',
          'Поређење мапе са стварним тлоцртом просторије.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Иста платформа као „Ђак за воланом“, друга способност: тамо возило прати научену стазу, овде разуме простор који први пут види. Заједно показују две гране аутономне вожње.',
      },
    ],
  },

  {
    slug: 'uspravno',
    broj: '09',
    naziv: 'Усправно',
    ikona: '🧍',
    kratko:
      'Камера са стране прати држање ученика за столом — угао врата и трупа, време погрбљености — и благо подсећа на исправљање. Само тачке тела, без слике.',
    status: 'предлог',
    boja: '#5FBA98',
    cvor: 'Усправно',
    pozicija: [-1.65, -1.73, -2.43],
    hardver: ['Raspberry Pi 5', 'Camera Module 3', 'LED / зујалица', 'Сет 37 у 1'],
    tehnologije: ['MediaPipe Pose', 'углови из кључних тачака', 'лична калибрација', 'Амбијентални фидбек'],
    uputstvo: 'uspravno-postavka',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/uspravno',
    telemetrija: {
      latencija: '~60 ms / кадру',
      npuCpu: 'Raspberry Pi 5 (CPU)',
      potrosnja: '~5 W',
      offline: '100% Офлајн',
      fps: '15 FPS',
      model: 'MediaPipe Pose (33 тачке)',
    },
    pipeline: [
      { icon: '📷', title: 'Camera Module 3', detail: 'Поглед са стране на ученика за столом' },
      { icon: '🧍', title: 'Детектор позе', detail: '33 кључне тачке тела, локално на Pi 5' },
      { icon: '📐', title: 'Рачун углова', detail: 'Угао врата и трупа у односу на усправно' },
      { icon: '⏱️', title: 'Тајмер погрбљености', detail: 'Минути ван доброг положаја, по часу' },
      { icon: '💡', title: 'Благ подсетник', detail: 'Светло или тон после дужег лошег држања' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Ученици сатима седе погнути над клупом, екраном и радним столом. Камера са стране прати држање, локално рачуна углове врата и трупа и мери колико времена по часу протекне у лошем положају. Кад погрбљеност потраје, благ подсетник — светло или тих тон.',
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Алат за освешћивање, не медицински уређај',
        text:
          'Систем не поставља дијагнозу — ни скалиозе ни кифозе. Мери навику држања и подсећа. Ако нешто упорно одступа, ученика треба упутити школском лекару. То пише и на самом уређају.',
      },
      { type: 'h', text: 'Лична калибрација' },
      {
        type: 'p',
        text:
          'На почетку часа ученик намести свој усправан положај и притисне дугме. Систем памти те углове као личну референцу и даље прати одступање од ње — не од неког просека. Тако ради и за виши и за нижи раст, и за различите столове.',
      },
      { type: 'h', text: 'Приватност уграђена у дизајн' },
      {
        type: 'p',
        text:
          'Слика се нигде не снима нити приказује. Из кадра се извуку само 33 тачке скелета, а на диск иду искључиво бројеви: углови и минути у лошем положају (`drzanje.csv`). Ништа по чему се особа може препознати.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'MediaPipe Pose даје 33 кључне тачке тела из сваког кадра (уво, раме, кук, колено…).',
          'Из тачака се рачунају два угла: врат (уво–раме у односу на вертикалу) и труп (раме–кук).',
          'Углови се пореде са личном референцом; ако пређу праг дуже од N секунди — то је „погрбљеност“.',
          'Свака погрбљеност се броји и мери; после задатог трајања укључи се LED или зујалица.',
          'На крају часа: колико пута, укупно минута, највећи угао — у CSV и на екрану.',
        ],
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'Raspberry Pi 5 (8 GB), активни хладњак',
          'Camera Module 3 (или USB веб камера), постављена са стране, у висини рамена',
          'Сет сензора „37 у 1“ (RGB LED, пасивна зујалица, тастер)',
          'Држач камере (3D штампа) за поновљив угао снимања',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Држач из 3D штампе није украс — ако се камера помери између часова, углови више нису упоредиви и мерење кроз недеље губи смисао.',
        data: {
          ploca: 'Raspberry Pi 5 (8 GB)',
          veze: [
            { port: 'CSI', ikona: '📷', naziv: 'Camera Module 3', detalj: 'са стране, у висини рамена' },
            { port: 'GPIO', ikona: '🪑', naziv: 'Стона конзола (37 у 1)', detalj: 'RGB амбијент, тиха зујалица и тастер' },
            { port: 'HDMI', ikona: '📊', naziv: 'Екран са графиком', detalj: 'углови и број погрбљености' },
            { port: 'USB-C', ikona: '🔌', naziv: 'Напајање 27 W', detalj: 'плоча и активни хладњак' },
          ],
        },
      },
      { type: 'h', text: 'Хардверска надградња (Сет 37 у 1)' },
      {
        type: 'p',
        text:
          'Уместо агресивних упозорења на екрану која ометају рад, на сто се поставља дискретна конзола са модулима из сета 37 у 1 за амбијентални фидбек:',
      },
      {
        type: 'steps',
        items: [
          'RGB LED (KY-016) на GPIO 17, 27, 22 — амбијентално светло: зелено/плаво за правилно седење, жуто за почетак погрбљености (< 15 s), црвено за упорно лоше држање (> 30 s).',
          'Пасивна зујалица (KY-006) на GPIO 24 — тих, нискотонски подсетник са постепеним успоном фреквенције који не омета остатак учионице.',
          'Тактилни тастер (KY-004) на GPIO 23 — брза рекалибрација: ученик седне усправно и притисне тастер за узимање референтних углова.',
          'Сензор нагиба (KY-020) на наслону столице — детектује када је ученик устао и спречава лажне аларме за празан сто.',
        ],
      },
      { type: 'h3', text: 'Шема повезивања (40-pin GPIO на Raspberry Pi 5)' },
      {
        type: 'code',
        lang: 'text',
        code: `        Raspberry Pi 5 GPIO Pinout
               ┌──────────────┐
  3.3V  (Pin 1)│ ●  ● │(Pin 2)  5V Power
               │ ●  ● │(Pin 6)  GND ─────────────► [GND] Заједничка маса
GPIO 17 (Pin 11)│ ●  ● │(Pin 12)
GPIO 27 (Pin 13)│ ●  ● │(Pin 14) GND
GPIO 22 (Pin 15)│ ●  ● │(Pin 16) GPIO 23 ────────► [S]   Калибрациони тастер (KY-004)
 3.3V  (Pin 17)│ ●  ● │(Pin 18) GPIO 24 ────────► [S]   Пасивна зујалица    (KY-006)
               │ ●  ● │(Pin 20) GND
GPIO 25 (Pin 22)│ ●  ● │(Pin 21)
               └──────────────┘

  Детаљна веза сигнала:
  ├── RGB LED амбијентални индикатор (KY-016):
  │     ├── R (Црвена) ────────► GPIO 17 (Pin 11)
  │     ├── G (Зелена) ────────► GPIO 27 (Pin 13)
  │     ├── B (Плава)  ────────► GPIO 22 (Pin 15)
  │     └── - (GND)    ────────► GND (Pin 6 или 14)
  │
  ├── Калибрациони тастер на столу (KY-004):
  │     ├── S (Сигнал) ────────► GPIO 23 (Pin 16)
  │     ├── VCC ───────────────► 3.3V (Pin 1 или 17)
  │     └── GND ───────────────► GND
  │
  └── Пасивна зујалица за благи тон (KY-006):
        ├── S (Сигнал PWM) ────► GPIO 24 (Pin 18)
        └── - (GND)    ────────► GND (Pin 20)`,
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Амбијентални фидбек и ергономија',
        text:
          'Амбијентални сигнали (благо светло на ивици стола и тих тон) доказано су ефикаснији од искачућих прозора на екрану јер не прекидају ток рада и пажњу, а суптилно освешћују правилно седење.',
      },
      { type: 'h3', text: 'Пример кода за проширење (без мењања постојећег кода)' },
      {
        type: 'p',
        text: 'Ученици могу креирати класу у src/drzanje/hardware_upgrade.py:',
      },
      {
        type: 'code',
        lang: 'python',
        code: `"""Амбијентални хардверски подсетник из сета 37 у 1 за пројекат Усправно."""
from __future__ import annotations
import logging
import time

log = logging.getLogger(__name__)

class DeskReminderHardware:
    """Управља амбијенталним RGB светлом, тихом зујалицом и тастером на столу."""

    def __init__(
        self,
        pin_r: int = 17,
        pin_g: int = 27,
        pin_b: int = 22,
        pin_btn: int = 23,
        pin_buzzer: int = 24,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._led = None
        self._btn = None
        self._buzzer = None

        if not enabled:
            return

        try:
            from gpiozero import RGBLED, Button, TonalBuzzer

            self._led = RGBLED(red=pin_r, green=pin_g, blue=pin_b)
            self._btn = Button(pin_btn, pull_up=True)
            self._buzzer = TonalBuzzer(pin_buzzer)

            log.info("Хардвер за праћење држања иницијализован.")
            self.set_posture("good")
        except Exception as exc:
            log.warning("GPIO недоступан (%s) — конзолни подсетник.", exc)
            self.enabled = False

    def is_calibrate_pressed(self) -> bool:
        """Враћа True ако ученик притиска тастер за рекалибрацију седења."""
        return bool(self._btn and self._btn.is_pressed)

    def set_posture(self, status: str) -> None:
        """Поставља амбијентално светло: 'good', 'warning' или 'slouch'."""
        if not self.enabled:
            return

        if status == "good":
            if self._led: self._led.color = (0, 0.4, 0.8)  # Смирујућа плава/зелена
            if self._buzzer: self._buzzer.stop()
        elif status == "warning":
            if self._led: self._led.color = (0.9, 0.5, 0)  # Топла жута
            if self._buzzer: self._buzzer.stop()
        elif status == "slouch":
            if self._led: self._led.color = (1, 0, 0)      # Црвена
            if self._buzzer:
                try:
                    self._buzzer.play("A4")                # Благи подсетник (440 Hz)
                    time.sleep(0.15)
                    self._buzzer.stop()
                except Exception:
                    pass

    def close(self) -> None:
        for dev in (self._led, self._btn, self._buzzer):
            if dev: dev.close()`,
      },
      { type: 'h3', text: 'Брзи тест на плочи' },
      {
        type: 'code',
        lang: 'bash',
        code: `python -c "
from gpiozero import RGBLED, Button; import time
led = RGBLED(17, 27, 22); btn = Button(23)
print('Усправно: плава LED...'); led.color = (0, 0.5, 1); time.sleep(1)
print('Опомена: жута LED...'); led.color = (1, 0.6, 0); time.sleep(1)
print('Погрбљено: црвена LED...'); led.color = (1, 0, 0); time.sleep(1); led.off()
print('Притисни калибрациони тастер (KY-004) на GPIO 23...')
if btn.wait_for_press(timeout=5):
    print('Тастер притиснут! Рекалибрација покренута.')
else:
    print('Време истекло.')
led.close(); btn.close()
"`,
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Где стоји камера',
        caption:
          'Камера гледа ученика са стране, не спреда — из профила се углови врата и трупа мере, а лице не улази у кадар.',
        data: {
          kamera: { naziv: 'Камера са стране', vfov: 52, visina: '≈ висина рамена' },
          zone: [
            { naziv: 'Мерни кадар — профил', od: 26, do: 76 },
          ],
          objekti: [
            { ikona: '🧍', naziv: 'Ученик у профилу', x: 52, y: 50 },
            { ikona: '🪑', naziv: 'Клупа', x: 76, y: 62 },
          ],
          tlo: 'Радно место у учионици — поглед одозго',
        },
      },
      { type: 'h', text: '„Скрининг“ режим (опционо, поглед спреда)' },
      {
        type: 'p',
        text:
          'Друга камера или преокренут сто: поглед спреда бележи разлику висине рамена и кукова кроз недеље и прави извештај. Извештај се носи школском лекару — систем и даље ништа не тврди, само даје бројке кроз време које човеку иначе промакну.',
      },
      { type: 'h', text: 'Наставна вредност' },
      {
        type: 'ul',
        items: [
          'Процена позе целог тела — иста породица као „Знаковна азбука“ (тачке шаке), други модел и примена.',
          'Геометрија: угао између вектора из кључних тачака, зашто нормализовати на висину рамена.',
          'Временски низови и прагови са хистерезом — да подсетник не „трепери“.',
          'Етика: разлика између скрининга и дијагнозе, зашто уређај не сме да тврди више него што зна.',
        ],
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Посетилац седне, калибрише се, па се погрби — уређај измери угао и после неколико секунди подсети.',
          'График држања кроз један школски час (симулиран или снимљен унапред).',
          'Јасна плоча: „ово мери навику, не болест“.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Здравље ученика техничке школе — сати за клупом, екраном и радним столом. Пројекат који школа може да покаже родитељима и који отвара разговор са школским диспанзером о превентиви.',
      },
    ],
  },

  {
    slug: 'pirotski-cilim',
    broj: '10',
    naziv: 'Шара у духу пиротског ћилима',
    ikona: '🧶',
    kratko:
      'Камера препозна шару на ћилиму и објасни је, а дифузиони модел на самој плочи компонује нову — па је претвори у картон за ткање, за школски разбој.',
    status: 'предлог',
    boja: '#D8AE45',
    cvor: 'Пиротски ћилим',
    pozicija: [0.35, -0.96, -2.38],
    hardver: ['Jetson Orin Nano (8 GB)', 'Logitech C922', 'NVMe SSD', 'екран на додир'],
    tehnologije: ['ViT класификатор', 'Stable Diffusion + ControlNet', 'TensorRT', 'сопствени скуп шара'],
    uputstvo: 'pirotski-cilim-postavka',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/pirotski-cilim',
    telemetrija: {
      latencija: '~4 s по шари',
      npuCpu: 'Orin Nano 8 GB (до 67 TOPS)',
      potrosnja: '~18 W',
      offline: '100% Офлајн',
      memorija: '~5 GB VRAM',
      model: 'SD 1.5 + ControlNet (TensorRT)',
    },
    pipeline: [
      { icon: '📷', title: 'C922 камера', detail: 'Ћилим или скица ученика под објективом' },
      { icon: '🔍', title: 'ViT класификатор', detail: 'Која је шара и у ком је делу ћилима' },
      { icon: '🎨', title: 'Дифузиони модел', detail: 'SD 1.5 + ControlNet води се скицом' },
      { icon: '📐', title: 'Правила клечања', detail: 'Симетрија, палета, пет појасева, два лица' },
      { icon: '🧵', title: 'Картон за ткање', detail: 'Мрежа са бројем нити и бојама — за разбој' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Школа има радионицу ћилима. Овај уређај стоји поред разбоја и ради две ствари: чита шару са готовог ћилима и објашњава је, па на основу скице ученика компонује нову шару по правилима заната — и избаци је као картон за ткање, мрежу коју ткаља стварно чита. Круг се затвара: ученици сликају, модел учи, модел предлаже, ученици ткају.',
      },
      { type: 'h', text: 'Зашто баш јачи уређај' },
      {
        type: 'p',
        text:
          'Осам пројеката програма ради на Raspberry Pi-ју, са малим моделима који нешто препознају. Овде је први пут модел који слику ствара, а не само чита — дифузиони модел. Stable Diffusion 1.5 са ControlNet-ом, преведен у TensorRT, даје шару 512×512 за неколико секунди на Orin Nano-у. На Pi-ју исти посао траје минутима, што уживо не значи ништа.',
      },
      { type: 'h', text: 'Грађа ћилима је правило, не украс' },
      {
        type: 'p',
        text:
          'Пиротски ћилим има пет јасних појасева: ресе, спољашњи ћенар, бордуру (плочу), унутрашњи ћенар и поље. Главне шаре иду у поље, бордура их уоквирује. Ткање техником клечања на вертикалном разбоју даје ћилим чија су оба лица потпуно иста — по томе се пиротски разликује од осталих балканских ћилима. Црвена преовлађује, у више нијанси.',
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Правила нису у моделу — правила су у коду',
        text:
          'Дифузиони модел не зна за клечање. Зато оно што избаци пролази кроз посебан модул: огледалска симетрија, квантизација на палету ћилима, пет појасева на својим местима, провера да се шара уопште може исткати. Тај модул нема ниједан неурон — може да се прочита, тестира и објасни.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'Ученици у радионици сликају ћилиме и разбој и означавају шаре у Label Studio-у — исти поступак као код „Знаковне азбуке“, други предмет.',
          'Мали ViT класификатор се дообучи на том скупу; из кадра препознаје шару и део ћилима у ком стоји.',
          'За стварање: ученик прстом повуче груб облик на екрану; ControlNet ту скицу држи као ограничење, а LoRA дообучена на школском скупу даје потез пиротске шаре.',
          'Пост-обрада намеће правила заната која модел иначе крши — симетрија, палета, појасеви.',
          'Излаз се дискретизује у картон за ткање: мрежа са индексом боје по пољу и бројем нити, у CSV и као слика за штампу.',
          'Ткаља погледа картон и каже шта је изводљиво. То што се исктка враћа се у скуп података.',
        ],
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Ово није „пиротски ћилим“ — то име је заштићено',
        text:
          '„Пиротски ћилим“ је од 2003. регистрована географска ознака (Завод за интелектуалну својину); право на то име имају само овлашћени произвођачи који раде по прописаном елаборату. Заштићено је име, не појединачан цртеж. Зато уређај свој излаз доследно зове „шара у духу пиротског ћилима“ — и то пише на самом уређају, као што „Усправно“ носи плочу „није медицински уређај“.',
      },
      { type: 'h', text: 'Шаре имају имена и значења' },
      {
        type: 'p',
        text:
          'Каталог броји преко стотину шара и орнамената. Корњача, која стоји и на грбу Пирота, значи дуг живот и постојаност; софра окупљање породице; ту су и гугутке, ђулови, венци, разгранато дрво, шкорпион, јеленак, куке, ченђели, Кондићева шара, престолонаследник. Списак и значења у пројекту потврђује радионица, уз проверу историјских назива код Музеја Понишавља — уређај не сме да измишља номенклатуру, зато свака непотврђена одредница носи ознаку.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'NVIDIA Jetson Orin Nano Developer Kit (8 GB)',
          'Logitech C922 Pro Stream изнад радне површине',
          'NVMe SSD за моделе (дифузиони модел је велик)',
          'Екран на додир — ту се црта скица и гледа резултат',
          'Активни хладњак и напајање 19 V',
          'Равномерно бочно осветљење — иначе сенка постане шара',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Екран је овде улаз, а не само излаз — на њему ученик црта скицу коју ControlNet држи као ограничење. Зато је на додир, а не обичан монитор.',
        data: {
          ploca: 'Jetson Orin Nano (8 GB)',
          veze: [
            { port: 'USB 3', ikona: '🎥', naziv: 'Logitech C922', detalj: 'ћилим и скица, 1080p аутофокус' },
            { port: 'M.2', ikona: '💽', naziv: 'NVMe SSD', detalj: 'SD 1.5, ControlNet, LoRA, каталог' },
            { port: 'DP', ikona: '🖐️', naziv: 'Екран на додир', detalj: 'скица улази, шара излази' },
            { port: 'USB', ikona: '🖨️', naziv: 'Штампач (по потреби)', detalj: 'картон за ткање на папиру' },
            { port: '19 V', ikona: '🔌', naziv: 'Напајање и хладњак', detalj: 'MAX-N режим тражи хлађење' },
          ],
        },
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Радно место поред разбоја',
        caption:
          'Камера гледа право надоле, светло долази са обе стране. Ако осветљење није равномерно, сенка између нити улази у слику као да је део шаре — исти проблем као код „Контроле квалитета“.',
        data: {
          kamera: { naziv: 'Камера изнад радне површине', vfov: 48, visina: '≈ 50 cm' },
          zone: [
            { naziv: 'Поље снимања — ћилим или скица', od: 28, do: 74 },
          ],
          objekti: [
            { ikona: '💡', naziv: 'Светло лево', x: 16, y: 48 },
            { ikona: '🧶', naziv: 'Ћилим', x: 50, y: 52 },
            { ikona: '💡', naziv: 'Светло десно', x: 84, y: 48 },
            { ikona: '🧵', naziv: 'Разбој', x: 50, y: 84 },
          ],
          tlo: 'Радионица ћилима — поглед одозго',
        },
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Модел лако нацрта шару коју је немогуће исткати',
        text:
          'Дифузиони модел даје мекане прелазе и косе линије којих у клечању нема. Картон за ткање зато увек проверава ткаља пре него што се прогласи употребљивим. Прва мера успеха пројекта није лепота слике него колико картона прође ту проверу.',
      },
      { type: 'h', text: 'Наставна вредност' },
      {
        type: 'ul',
        items: [
          'Генеративни модели изблиза: латентни простор, кораци уклањања шума, ControlNet као ограничење.',
          'Разлика између препознавања и стварања — једини пројекат где ученици раде обоје.',
          'Квантизација и TensorRT: иста тема као код „Школског асистента“, други модел.',
          'Правила заната као кôд: како се традиција записује у функцију која се тестира.',
          'Интелектуална својина и AI: шта значи географска ознака и зашто уређај пази како назива свој излаз.',
          'Сопствени скуп података и његова етика — чије је наслеђе и ко даје сагласност.',
        ],
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Посетилац прстом повуче облик — уређај за неколико секунди врати шару у духу ћилима.',
          'Уређај чита шару са донетог ћилима и каже јој име и значење.',
          'Зид: скица → шара коју је модел дао → картон за ткање → комад који су ученици исткали.',
          'Бројка која се мери: колико предлога је ткаља прогласила изводљивим.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Ћилим је визуелни симбол града — корњача са ћилима стоји на грбу Пирота. Пиротско ћилимарство је 18. јуна 2012. уписано у Национални регистар нематеријалног културног наслеђа Србије. Ово је једини пројекат програма који спаја технолошку школу са оним по чему је град познат, и једини у ком уређај не служи струци него занату који је ту већ вековима.',
      },
    ],
  },

  {
    slug: 'dvojnik',
    broj: '11',
    naziv: 'Двојник',
    ikona: '🗿',
    kratko:
      'Ставиш предмет на окретни сто, камера га обиђе у круг, Orin од силуета сложи 3D модел — и школски штампач одштампа копију.',
    status: 'предлог',
    boja: '#60A5FA',
    cvor: 'Двојник',
    pozicija: [-0.1, 0.21, 2.3],
    hardver: ['Jetson Orin Nano (8 GB)', 'Logitech C922', 'окретни сто са корачним мотором', '3D штампач'],
    tehnologije: ['space carving', 'CUDA без мреже', 'marching cubes', 'извоз у STL'],
    uputstvo: 'dvojnik-postavka',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/dvojnik',
    telemetrija: {
      latencija: '~40 s по предмету',
      npuCpu: 'Orin Nano — 1024 CUDA језгра',
      potrosnja: '~14 W',
      offline: '100% Офлајн',
      mreza: 'воксели 256³',
      izlaz: 'STL за штампу',
    },
    pipeline: [
      { icon: '🔄', title: 'Окретни сто', detail: 'Корачни мотор — угао сваког кадра је познат' },
      { icon: '📷', title: 'C922 камера', detail: '120 кадрова, сваки на 3° заокрета' },
      { icon: '✂️', title: 'Издвајање силуете', detail: 'Предмет од позадине, кадар по кадар' },
      { icon: '🧊', title: 'Резбарење воксела', detail: 'Свака силуета одсече вишак — на CUDA језгрима' },
      { icon: '🖨️', title: 'Мрежа и STL', detail: 'Троуглови из воксела → фајл за штампач' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Посетилац донесе предмет и стави га на окретни сто. Сто се врти, камера снима, а на екрану у ходу расте тродимензионални модел који се може окренути и измерити. На крају излази STL фајл — школски 3D штампач одштампа копију. Донео си предмет, одлазиш са његовим двојником.',
      },
      { type: 'h', text: 'Зашто окретни сто мења цео пројекат' },
      {
        type: 'p',
        text:
          'Класично 3D скенирање тражи да систем сам погоди где је камера била у сваком тренутку. Тај корак (визуелна одометрија) губи траг на једнобојном предмету, при брзом покрету и на сјајној површини — и ту већина школских покушаја пропадне. Окретни сто тај проблем брише: корачни мотор се окреће за тачно познат угао, па се положај не процењује него зна. Исти принцип као сигурносни слој код „Ђака за воланом“ — не процењуј оно што можеш да измериш.',
      },
      { type: 'h', text: 'Како ради' },
      {
        type: 'steps',
        items: [
          'Прво се сними празна позадина, без предмета — то је референца.',
          'Сто се окреће за 3° и стаје; камера сними кадар. Тако 120 пута, до пуног круга.',
          'У сваком кадру се предмет одвоји од позадине — добија се силуета, црно-бела маска.',
          'Радни простор је коцка воксела. За сваки кадар се сваки воксел пројектује у слику: ако падне ван силуете, реже се. После пуног круга остаје само оно што је у свакој силуети било „унутра“.',
          'Од преосталих воксела се склопи мрежа троуглова и упише као STL.',
          'Ученик измери праву висину предмета шублером и упише је — модел се скалира да се поклопи. Тек тада штампа излази у правој величини.',
        ],
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Овде GPU не рачуна неуронску мрежу',
        text:
          'Резбарење воксела је чиста геометрија — милиони независних пројекција, сваки воксел за себе. Управо оно за шта су CUDA језгра направљена. Ово је једини пројекат програма у ком ученици виде зашто је графички процесор брз, а да у томе нема ниједног неурона.',
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Шта овај метод не може — и то је математика, не квар',
        text:
          'Од силуета се добија „визуелни омотач“: најмање тело које баца исте сенке. Прво, удубљење које се са стране не види — унутрашњост шоље, рупа на врху — остаје попуњено; шоља испадне пун ваљак. Друго, висина се благо прецени, јер су сви кадрови снимљени са исте висине камере, па воксел изнад предмета са супротне стране пада у исти део слике као његов врх. Водоравне мере су тесне, њих сто обиђе у круг. Обе границе имају свој тест, а не фусноту.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'NVIDIA Jetson Orin Nano Developer Kit (8 GB)',
          'Logitech C922 на непомичном сталку',
          'Окретни сто: корачни мотор 28BYJ-48 + ULN2003 драјвер (плоча 3D штампана)',
          'Матирана позадина у контрастној боји',
          'Дифузно осветљење са обе стране, непроменљиво',
          'Шублер — без мерења нема праве величине',
          '3D штампач који школа већ има',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Кључна веза је GPIO ка мотору: софтвер зна за колико се сто окренуо јер је сам то наредио. Зато у ланцу нема ниједног корака који погађа положај камере.',
        data: {
          ploca: 'Jetson Orin Nano (8 GB)',
          veze: [
            { port: 'USB 3', ikona: '🎥', naziv: 'Logitech C922', detalj: 'непомична, гледа сто са стране' },
            { port: 'GPIO', ikona: '🔄', naziv: 'ULN2003 → мотор', detalj: 'корак = познат угао' },
            { port: 'DP', ikona: '🧊', naziv: 'Екран', detalj: 'модел расте уживо, може да се окрене' },
            { port: 'USB', ikona: '🖨️', naziv: 'STL на штампач', detalj: 'преко картице или мреже' },
            { port: '19 V', ikona: '🔌', naziv: 'Напајање и хладњак', detalj: 'резбарење оптерети GPU' },
          ],
        },
      },
      {
        type: 'shema',
        kind: 'scena',
        naslov: 'Радно место',
        caption:
          'Камера гледа сто са стране, мало одозго — тако види и обрис и горњу ивицу предмета. Позадина мора бити једнобојна и матирана: сјајна позадина даје одсјај који издвајање силуете чита као део предмета.',
        data: {
          kamera: { naziv: 'Камера са стране', vfov: 54, visina: '≈ 25 cm' },
          zone: [
            { naziv: 'Радни простор — коцка воксела', od: 34, do: 70 },
          ],
          objekti: [
            { ikona: '💡', naziv: 'Светло лево', x: 16, y: 44 },
            { ikona: '🗿', naziv: 'Предмет на столу', x: 50, y: 52 },
            { ikona: '💡', naziv: 'Светло десно', x: 84, y: 44 },
            { ikona: '🎞️', naziv: 'Позадина', x: 50, y: 20 },
          ],
          tlo: 'Сто за скенирање — поглед одозго',
        },
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Скенер нема осећај за величину',
        text:
          'Из слика се добија облик, не мере. Док се не унесе једна права дужина — висина предмета са шублера — модел може бити и напрстак и буре. То је најбоља лекција пројекта: једна измерена бројка вреди више од сто кадрова.',
      },
      { type: 'h', text: 'Наставна вредност' },
      {
        type: 'ul',
        items: [
          'Геометрија рачунарског вида: пројекција тачке кроз камеру, спољашњи и унутрашњи параметри.',
          'Зашто је GPU брз — на задатку који је очигледно паралелан, без мреже.',
          'Визуелни омотач и његова граница: шта се из силуета може, а шта не може сазнати.',
          'Размера и калибрација: систем без мерења нема величину.',
          'Спој са 3D штампом коју школа већ има — од кадра до предмета у руци.',
        ],
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Посетилац донесе предмет, за минут га види као модел који се врти на екрану.',
          'Поред стоји већ одштампан двојник претходног предмета — оригинал и копија један до другог.',
          'Табла са шољом: зашто јој унутрашњост остаје пуна.',
          'Мерење: одштампана копија на шублеру, одступање у милиметрима.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Пар са „Шаром у духу пиротског ћилима“: тамо машина смисли шару па је ученици исткају, овде машина сними предмет па га штампач изведе. Оба пројекта затварају исти круг — од рачунара до нечега што се може узети у руке. За школу је ово и употребљив алат: резервни део који се више не производи довољно је ставити на сто.',
      },
    ],
  },

  {
    slug: 'ziva-rec',
    broj: '12',
    naziv: 'Жива реч',
    ikona: '🗣️',
    kratko:
      'Теренска станица која снима пиротски говор у кући говорника, транскрибује на лицу места и одмах даје да се исправи — без мреже.',
    status: 'предлог',
    boja: '#C77DFF',
    cvor: 'Жива реч',
    pozicija: [-2.5, -0.57, -1.55],
    hardver: ['Jetson Orin Nano (8 GB)', 'добар USB микрофон', 'слушалице', 'повербанк'],
    tehnologije: ['faster-whisper', 'мерење торлачних црта (правила)', 'корпус са сагласношћу', 'дообука на терену'],
    uputstvo: 'ziva-rec-postavka',
    repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/ziva-rec',
    telemetrija: {
      latencija: '~1× трајање снимка',
      npuCpu: 'Orin Nano 8 GB (CUDA)',
      potrosnja: '~12 W',
      offline: '100% Офлајн',
      model: 'Whisper large-v3-turbo (int8)',
      izlaz: 'поравнати парови (звук, текст)',
    },
    pipeline: [
      { icon: '🎙️', title: 'USB микрофон', detail: 'Глас говорника, 16 kHz — остаје на уређају' },
      { icon: '🧠', title: 'Whisper int8', detail: 'Препис на српском — намерно лош на дијалекту' },
      { icon: '📐', title: 'Мерење црта', detail: 'Правила: полугласник, /ѕ/, по-/нај-, члан, аорист' },
      { icon: '✍️', title: 'Исправка', detail: 'Говорник поправља сегмент по сегмент' },
      { icon: '📚', title: 'Корпус', detail: 'Пар (исечак, текст) + ко + сагласност' },
    ],
    sadrzaj: [
      {
        type: 'p',
        lead: true,
        text:
          'Уређај се носи код баке, где интернета нема. Сними како она прича, транскрибује на лицу места, и одмах јој на екрану покаже препис да га исправи. Исправљени парови — исечак снимка и тачан текст — остају на уређају и, кад их скупи довољно, служе да се Whisper дообучи да боље разуме пиротски.',
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Чет-бот који „зна“ пиротски је засебан, каснији пројекат',
        text:
          'Ова станица само прикупља грађу. Мали модел са мало података измишља дијалекат — лажне речи, лажну граматику — а код угроженог језика то није безазлено. Права вредност није модел него корпус који иза њега расте.',
      },
      { type: 'h', text: 'Зашто баш на уређају, а не у облаку' },
      {
        type: 'p',
        text:
          'Пиротски говор (тимочко-лужнички дијалекат) део је торлачке групе, коју UNESCO води као угрожен језик. Снимаш глас старе особе у њеној кући. Слање тога на туђи сервер је тачно оно што се не сме. Ниједан други пројекат програма нема тако чист разлог да буде офлајн.',
      },
      { type: 'h', text: 'Три ствари које станица не сме' },
      {
        type: 'ul',
        items: [
          'Модел не измишља — транскрипт је полазна тачка за исправку коју ради говорник, не тврдња о томе како се шта каже.',
          'Речник не измишља — свака одредница носи извор (Златковићев „Речник пиротског говора“, снимак, литература); непотврђено се исписује са оградом.',
          'Приватност — снимак остаје на уређају док говорник не одобри унос; извоз за дообуку прескаче све без сагласности.',
        ],
      },
      { type: 'h', text: 'Мерење торлачности — правила, не модел' },
      {
        type: 'p',
        text:
          'Посебан модул мери колико је реченица дијалекатска: чуван полугласник (със, съга), африката /ѕ/, аналитички компаратив (по-убав, нај-убав), постпозитивни члан (човекат, детето), изгубљено /х/ (леб, оћу), аорист и имперфекат, футур са „че“. Свака црта има пример, тежину и тест. Намерно је груба — служи да се издвоје јако дијалекатски сегменти за исправку и да се провери да дообучени Whisper није „упеглао“ говор ка стандарду.',
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Постоји подлога, не креће се од нуле',
        text:
          'Златковићев речник (~33.000 речи, 50 година рада), говорни корпус торлачког (Вуковић и сар.), Torlak ReLDI означивач врсте речи, и рад Tang & Vuković са COLING 2025 који је радио тачно ово. Приче Мијалка Расничког (Ћирић и Панајотовић) су објављена пиротска проза која, уз дозволу, може да засеје корпус.',
      },
      { type: 'h', text: 'Хардвер' },
      {
        type: 'specs',
        items: [
          'NVIDIA Jetson Orin Nano Developer Kit (8 GB)',
          'Добар USB микрофон — за старије гласове важнији од камере',
          'Слушалице — говорник чује свој снимак при исправци',
          'Повербанк за рад на терену',
          'Екран на додир или лаптоп за исправку',
        ],
      },
      {
        type: 'shema',
        kind: 'hardver',
        naslov: 'Шема повезивања',
        caption:
          'Најмања станица у програму која носи Jetson — микрофон, слушалице, екран. Ниједан кабл не иде ка мрежи; то је суштина, не штедња.',
        data: {
          ploca: 'Jetson Orin Nano (8 GB)',
          veze: [
            { port: 'USB', ikona: '🎙️', naziv: 'USB микрофон', detalj: '16 kHz, глас говорника' },
            { port: '3.5 mm', ikona: '🎧', naziv: 'Слушалице', detalj: 'говорник слуша свој снимак' },
            { port: 'DP', ikona: '✍️', naziv: 'Екран за исправку', detalj: 'сегмент по сегмент' },
            { port: 'M.2', ikona: '💽', naziv: 'NVMe SSD', detalj: 'Whisper и корпус' },
            { port: 'USB-C', ikona: '🔋', naziv: 'Повербанк', detalj: 'рад на терену, без мреже' },
          ],
        },
      },
      {
        type: 'callout',
        tone: 'alert',
        title: 'Сагласност и рад са говорницима',
        text:
          'Сними реченицу у којој говорник каже да пристаје — то је први унос у сесији. Само иницијали и село, деценија рођења уместо датума. Говорник у сваком тренутку може да каже „избришите то“. Детаљно у projekti/ziva-rec/docs/etika.md.',
      },
      { type: 'h', text: 'Наставна вредност' },
      {
        type: 'ul',
        items: [
          'Дијалектологија као подаци: које се црте пиротског говора могу мерити и како.',
          'Дообука готовог модела на малом сопственом скупу — и замка да „поправи“ оно што треба да сачува.',
          'Подела скупа по говорницима, не по исечцима — иначе модел научи глас, не говор.',
          'Етика рада са угроженим језиком и старим људима: сагласност, приватност, право на брисање.',
        ],
      },
      { type: 'h', text: 'Резултат за Demo Day' },
      {
        type: 'ul',
        items: [
          'Посетилац изговори реченицу на пиротском — станица измери колико је дијалекатска и означи сваку црту.',
          'Уживо: стандардни Whisper меље „лебац“ у „хлеб“, а дообучени га задржи.',
          'График: WER стандардног модела наспрам дообученог, кроз недеље снимања.',
          'Бројка која се мери: сати одобреног звука у корпусу.',
        ],
      },
      { type: 'h', text: 'Веза са Пиротом' },
      {
        type: 'p',
        text:
          'Пиротски говор нестаје са својим говорницима. Ово је једини пројекат у ком уређај не решава задатак него бележи нешто што ће иначе бити изгубљено — а школа у Пироту је на најбољем могућем месту да то уради.',
      },
    ],
  },
]

export const rezervneIdeje = [
  {
    naziv: 'Сортирница амбалаже',
    tekst:
      '3D штампана трака и серво рука разврставају PET, алуминијум и папир. Визуелно најефектније, али тражи највише механике.',
  },
  {
    naziv: 'Саобраћај и ваздух',
    tekst:
      'Број возила из „Паметне зебре“ укрштен са мерењима BME688 сензора — веза густине саобраћаја и квалитета ваздуха у Пироту.',
  },
  {
    naziv: 'Бројач понављања на часу физичког',
    tekst:
      'Процена позе броји чучњеве и згибове. Популарно код ученика, слабија научна прича.',
  },
]

export const getProjekat = (slug) => projekti.find((p) => p.slug === slug)
