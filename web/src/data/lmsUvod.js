/* Уводне лекције („Предзнање") — за оне којима недостаје Python, NumPy, OpenCV или
   рад на Pi-ју. Нису предуслов за лекције 1–7; лекција 1 их само препоручује.
   Ознака у интерфејсу је „Увод N" (види `oznaka` у lms.js). */

export const uvodLekcije = [
  {
    slug: 'okruzenje-pi-ssh-venv',
    grupa: 'uvod',
    redosled: 1,
    naziv: 'Окружење: Pi, SSH, venv',
    kratko: 'Како да се повежеш на Raspberry Pi, активираш Python окружење и покренеш пример.',
    nivo: 'основно',
    vreme: '30 мин',
    preduslov: null,
    uputstva: ['raspberry-pi-priprema'],
    ishodi: [
      'повежеш се на Pi преко SSH-а и разумеш разлику између рада на Pi-ју и на свом рачунару',
      'активираш виртуелно окружење и знаш по чему видиш да је активно',
      'покренеш и зауставиш пример, и објасниш зашто једну камеру може да користи само једна апликација',
    ],
    primeri: [],
    projekti: [],
    sadrzaj: [
      { type: 'p', lead: true, text: 'Већина „грешака" на првом часу нису грешке у коду, већ у окружењу: погрешан фолдер, неактивно окружење, камера коју већ користи други програм. Овде их све решаваш једном.' },
      { type: 'h', text: 'Pi је други рачунар' },
      { type: 'p', text: 'Pi често нема свој екран и тастатуру у твојим рукама. Зато се на њега повезујеш преко мреже: SSH ти даје терминал на Pi-ју, а у њему куцаш команде као да седиш пред њим. Припрема плочице (ОС, лозинка, SSH) је у упутству „Припрема Raspberry Pi 5".' },
      { type: 'code', lang: 'bash', code: 'ssh korisnik@ime-uredjaja.local' },
      { type: 'h', text: 'Виртуелно окружење' },
      { type: 'p', text: 'Python библиотеке (OpenCV, MediaPipe, NumPy…) инсталиране су у посебан фолдер, а не у цео систем. То се зове виртуелно окружење (venv). Док га не активираш, команда python га не види и примери јављају да нешто није инсталирано.' },
      {
        type: 'code',
        lang: 'bash',
        code: `source ~/primeri/env/bin/activate     # или: source ~/venv/bin/activate
# на почетку реда мора да пише (venv) или (env)
which python                          # путања треба да води у окружење
deactivate                            # када завршиш`,
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Која путања?',
        text: 'У pokretanje.txt стоје обе: ~/venv и ~/primeri/env. Покретач (pokreni.sh) користи /home/pi/primeri/env, па је то подразумевано окружење за примере.',
      },
      { type: 'h', text: 'Покретање примера' },
      {
        type: 'code',
        lang: 'bash',
        code: `cd ~/primeri/test
python check_cam.py

# недостаје библиотека?
pip install pyserial`,
      },
      { type: 'p', text: 'Команде pip install ради само док је окружење активно. Примери који су зависни од MediaPipe-а траже одређену верзију, а сами исписују тачну команду када је нема (на пример pip install mediapipe==0.10.14).' },
      { type: 'h', text: 'Прозор на ТВ-у, а команде преко SSH-а' },
      { type: 'p', text: 'Када већину примера покренеш преко SSH-а, они сами постављају DISPLAY=:0 и WAYLAND_DISPLAY=wayland-0, па се прозор појављује на екрану прикљученом на Pi, а не на твом рачунару. Ако нема екрана, покретач се може користити у текстуалном режиму.' },
      {
        type: 'code',
        lang: 'bash',
        code: `cd ~/primeri
./pokreni.sh              # прозор ако има екрана, иначе текстуални мени
python pokretac.py --cli  # текстуални мени преко SSH-а`,
      },
      { type: 'h', text: 'Излаз и камера' },
      {
        type: 'steps',
        items: [
          'Прозор примера се затвара тастером [q] или [ESC] (док је прозор у фокусу).',
          'Ако је програм у терминалу, прекида се са Ctrl+C.',
          'Камеру у исто време може да користи само један програм. Ако нова апликација јави да камера није пронађена, прво провери да ли је претходна заиста затворена. Покретач то ради уместо тебе кад мењаш игру.',
          'Ако примери предложе „libcamerify python …", то је њихов савет када Picamera2 не успе да нађе камеру.',
        ],
      },
      {
        type: 'shema',
        kind: 'tok',
        naslov: 'Од твог рачунара до прозора на ТВ-у',
        caption: 'Куцаш на свом рачунару, програм ради на Pi-ју, а слика излази на екран прикључен на Pi.',
        pipeline: [
          { icon: '💻', title: 'Твој рачунар', detail: 'терминал, ssh …' },
          { icon: '🌐', title: 'Мрежа', detail: 'иста Wi-Fi или кабл' },
          { icon: '🍓', title: 'Raspberry Pi 5', detail: 'venv, python пример.py' },
          { icon: '📺', title: 'HDMI екран', detail: 'DISPLAY=:0 — прозор овде' },
        ],
      },
      { type: 'h', text: 'Вежба' },
      {
        type: 'steps',
        items: [
          'Повежи се на Pi преко SSH-а и испиши pwd.',
          'Активирај окружење и провери да се на почетку реда појавило (venv) или (env).',
          'Покрени python -c "import cv2; print(cv2.__version__)". Ради ли без активираног окружења?',
          'Покрени cd ~/primeri/test && python check_cam.py и забележи ипис.',
        ],
      },
    ],
  },

  {
    slug: 'python-za-pocetnike',
    grupa: 'uvod',
    redosled: 2,
    naziv: 'Python за оне који већ програмирају',
    kratko: 'Само оно из Python-а што је потребно да прочиташ и измениш примере: петље, функције, листе, речници, класе.',
    nivo: 'основно',
    vreme: '40 мин',
    preduslov: null,
    ishodi: [
      'прочиташ типичну петљу игре и препознаш где се чита кадар, а где црта',
      'разликујеш листу, торку и речник и знаш која се где користи у примерима',
      'прочиташ функцију и класу из примера и измениш у њој једну вредност',
      'објасниш чему служи try/except око import-а',
    ],
    primeri: [],
    projekti: [],
    sadrzaj: [
      { type: 'p', lead: true, text: 'Ако већ програмираш на другом језику, ово ти је преглед разлика. Свака ставка је узета из кода примера, па ћеш је касније препознати.' },
      { type: 'h', text: 'Променљиве и типови' },
      {
        type: 'code',
        lang: 'python',
        code: `EAR_THRESHOLD = 0.22        # float
broj_balona = 5             # int
ime = "Pirot"               # str
aktivan = True              # bool
rezultat = None             # "ништа" (још нема вредности)
print(f"Prag: {EAR_THRESHOLD}, balona: {broj_balona}")`,
      },
      { type: 'p', text: 'Типови се не наводе. Велика слова по договору означавају константу (праг који не мењаш током рада). Блокови се одређују увлачењем, не витичастим заградама.' },
      { type: 'h', text: 'Гранање' },
      {
        type: 'code',
        lang: 'python',
        code: `if closed_duration >= 1.3:
    status = "ALARM"
elif mar > 0.55:
    status = "ZEVANJE"
else:
    status = "OK"`,
      },
      { type: 'h', text: 'Петља игре' },
      { type: 'p', text: 'Свака апликација са камером је бесконачна петља која се прекида када притиснеш тастер. Унутар ње: узми кадар, обради, нацртај, прикажи.' },
      {
        type: 'code',
        lang: 'python',
        code: `while True:
    kadar = uzmi_kadar()
    # ... обрада и цртање ...
    kljuc = cv2.waitKey(1) & 0xFF
    if kljuc == ord("q"):
        break

for tip in [8, 12, 16, 20]:     # for иде по елементима
    print(tip)`,
      },
      { type: 'h', text: 'Функције' },
      {
        type: 'code',
        lang: 'python',
        code: `def calc_ear(landmarks, eye_indices, w, h):
    # ... рачуна ...
    return (d_v1 + d_v2) / (2.0 * d_h)

ear = calc_ear(lm, RIGHT_EYE, 640, 480)`,
      },
      { type: 'h', text: 'Листе, торке, речници' },
      {
        type: 'code',
        lang: 'python',
        code: `finger_tips = [4, 8, 12, 16, 20]      # листа: може да се мења
tacka = (320, 240)                    # торка: пар (x, y), не мења се
finger_tips[1:]                       # [8, 12, 16, 20] — резање, без палца
x, y = tacka                          # распакивање

recnik = {"кво": "шта", "оти": "зашто"}   # речник: кључ → вредност
recnik["саг"] = "сад"
points = {}
points[110] = (2600, 15)              # као у lidar.py: угао → (удаљеност, квалитет)

pts = [t * 2 for t in finger_tips]    # листа из петље (comprehension)`,
      },
      { type: 'h', text: 'Класе' },
      { type: 'p', text: 'Игре чувају сваки балон, атом или звездицу као објекат: податке и понашање заједно. __init__ се позива при прављењу, self је сам објекат. Ово је упрошена верзија класе Balloon из baloni.py:' },
      {
        type: 'code',
        lang: 'python',
        code: `class Balloon:
    def __init__(self):
        self.x = 320
        self.y = 480
        self.r = 30

    def update(self):
        self.y -= 3                      # балон се пење

    def is_touching(self, px, py):
        return (px - self.x) ** 2 + (py - self.y) ** 2 < self.r ** 2

b = Balloon()
b.update()
print(b.is_touching(320, 477))`,
      },
      { type: 'h', text: 'import и try/except' },
      {
        type: 'code',
        lang: 'python',
        code: `import os
import numpy as np
import cv2

try:
    import mediapipe as mp
except ImportError:
    print("mediapipe nije instaliran!")
    exit(1)

os.environ["DISPLAY"] = ":0"          # променљиве окружења`,
      },
      { type: 'p', text: 'try/except се јавља на почетку многих примера: уместо дугог иписа грешке, програм каже шта недостаје и како да се инсталира.' },
      {
        type: 'callout',
        tone: 'info',
        title: 'Најчешћа грешка: увлачење',
        text: 'Python не користи { }. Ако кôд у петљи није увучен једнако (4 размака), добијаш IndentationError. Не мешај табулаторе и размаке.',
      },
      { type: 'h', text: 'Вежба' },
      {
        type: 'steps',
        items: [
          'Налепи класу Balloon у фајл balloon.py, па на крај додај петљу која 5 пута позове update() и испише b.y.',
          'Направи речник са три пиротске речи и испиши значење речи коју корисник унесе (input()).',
          'У петљи while True додај бројач који ће прекинути петљу после 100 корака.',
        ],
      },
    ],
  },

  {
    slug: 'numpy-i-nizovi',
    grupa: 'uvod',
    redosled: 3,
    naziv: 'NumPy и низови',
    kratko: 'Кадар је низ. Облик, индексирање, резање, маске и np.where — све што користе лекције 1 и 5.',
    nivo: 'основно',
    vreme: '45 мин',
    preduslov: 'python-za-pocetnike',
    ishodi: [
      'прочиташ shape и dtype низа и знаш да је редослед (висина, ширина, канали)',
      'издвојиш канал или правоугаону област кадра',
      'направиш логичку маску и њоме замениш пикселе са np.where',
      'знаш зашто 8-битни низ може да прелије (200 + 100 даје 44)',
    ],
    primeri: ['numpy-kadar'],
    projekti: [],
    sadrzaj: [
      { type: 'p', lead: true, text: 'У лекцији 1 кадар је био „низ облика (480, 640, 3)". Овде видиш шта то значи у пракси: како се чита, реже и мења. Све ради без камере, на чистом NumPy-ју.' },
      { type: 'h', text: 'Облик и тип' },
      {
        type: 'code',
        lang: 'python',
        code: `import numpy as np

kadar = np.zeros((480, 640, 3), dtype=np.uint8)
print(kadar.shape)     # (480, 640, 3) — висина, ширина, канали
print(kadar.dtype)     # uint8 — цели бројеви 0..255`,
      },
      { type: 'h', text: 'Индексирање: прво ред (y), па колона (x)' },
      {
        type: 'code',
        lang: 'python',
        code: `kadar[240, 320] = (255, 255, 255)        # [ред, колона] = [y, x]
kadar[:, :, 0].max()                      # само први канал (индекс 0)
kadar[100:200, 300:500] = (0, 165, 255)   # резање: ред 100–199, колоне 300–499
isecak = kadar[120:180, 320:480]          # исечак, облик (60, 160, 3)
isecak.mean(axis=(0, 1))                  # просек по сваком каналу`,
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Пази на редослед',
        text: 'У тачки (x, y) на екрану иде прво x, а у низу прво y: кадар[y, x]. Ово је најчешћи узрок „слика је окренута за 90°".',
      },
      { type: 'h', text: 'Маска и np.where' },
      { type: 'p', text: 'Поређење низа даје низ тачно/нетачно исте величине — маску. np.where(услов, а, б) на сваком месту узима „а" где је услов тачан, иначе „б". Тако пример „Пуцкетање" брише особу из кадра.' },
      {
        type: 'code',
        lang: 'python',
        code: `maska = kadar[:, :, 2] > 128                 # 2D: (480, 640) — црвено јаче од 128
siva = np.full_like(kadar, 90)
maska_3d = np.dstack((maska, maska, maska))   # исти облик као кадар: (480, 640, 3)
rezultat = np.where(maska_3d, siva, kadar)    # где је маска → сива, иначе кадар`,
      },
      {
        type: 'shema',
        kind: 'tok',
        naslov: 'Како настаје замена пиксела',
        caption: 'Маска мора да има исти облик као кадар. Зато се 2D маска слаже у три копије (dstack) пре np.where.',
        pipeline: [
          { icon: '🔢', title: 'Кадар', detail: 'облик (480, 640, 3)' },
          { icon: '❓', title: 'Услов', detail: 'канал > 128 → маска (480, 640)' },
          { icon: '🥞', title: 'np.dstack', detail: 'маска (480, 640, 3)' },
          { icon: '🔀', title: 'np.where', detail: 'нова вредност где је маска' },
        ],
      },
      { type: 'h', text: 'Прелив: 200 + 100 није 300' },
      { type: 'p', text: 'uint8 памти само 0 до 255. Збир који премаши 255 „прелије" и враћа се од нуле. Зато се боје множе (као у apply_noir_balance) тек пошто се кадар претвори у float32, па се врати у границе помоћу np.clip.' },
      {
        type: 'code',
        lang: 'python',
        code: `a = np.array([200], dtype=np.uint8)
print(a + 100)                                   # [44] — прелив!

f = a.astype(np.float32) * 1.5
print(np.clip(f, 0, 255).astype(np.uint8))       # [255] — безбедно`,
      },
      { type: 'h', text: 'Вежба' },
      {
        type: 'steps',
        items: [
          'Покрени python numpy_kadar.py и упореди ипис са кодом: који ред даје који ипис?',
          'Промени боју правоугаоника из (0, 165, 255) у (255, 0, 0). Колико је сада пиксела у маски и зашто?',
          'Направи маску за плави канал (индекс 0) и замени те пикселе белом бојом.',
          'Убаци a + 100 за 200 у uint8 и у float32. Објасни разлику.',
        ],
      },
    ],
  },

  {
    slug: 'opencv-osnove',
    grupa: 'uvod',
    redosled: 4,
    naziv: 'OpenCV основе',
    kratko: 'Учитај слику, нацртај по њој, промени боје и састави најмању петљу са камером.',
    nivo: 'основно',
    vreme: '50 мин',
    preduslov: 'numpy-i-nizovi',
    ishodi: [
      'учиташ и прикажеш слику и затвориш прозор тастером',
      'нацрташ линију, круг, правоугаоник и текст у BGR боји',
      'претвориш боје (BGR у сиво, RGB и HSV) и знаш када је које потребно',
      'саставиш најмању петљу са камером: кадар, flip, FPS, излаз на [q]',
    ],
    primeri: ['opencv-slika', 'opencv-kamera'],
    projekti: [],
    sadrzaj: [
      { type: 'p', lead: true, text: 'OpenCV је библиотека за слике. За све наше примере треба вам само мали део: учитавање, цртање, претварање боја и петља са прозором.' },
      { type: 'h', text: 'Слика је NumPy низ' },
      {
        type: 'code',
        lang: 'python',
        code: `import cv2

slika = cv2.imread("logo.png")        # BGR, облик (висина, ширина, 3)
print(slika.shape)
cv2.imshow("Прозор", slika)
cv2.waitKey(0)                        # чека на било који тастер
cv2.destroyAllWindows()`,
      },
      {
        type: 'callout',
        tone: 'warn',
        title: 'Путања са č, š, ž на Windows-у',
        text: 'cv2.imread не отвара путање са таквим словима (наш пројектни фолдер их има). Решење које ради свуда: cv2.imdecode(np.fromfile(путања, dtype=np.uint8), cv2.IMREAD_COLOR). На Pi-ју то обично није проблем.',
      },
      { type: 'h', text: 'Боје су BGR' },
      { type: 'p', text: 'OpenCV држи канале као плаво, зелено, црвено. Боја (0, 0, 255) је зато црвена, а не плава. Тачке се дају као (x, y), а дебљина -1 значи „попуни".' },
      {
        type: 'code',
        lang: 'python',
        code: `cv2.line(slika, (10, 10), (200, 200), (0, 0, 255), 2)        # црвена линија
cv2.circle(slika, (100, 100), 40, (0, 255, 0), 3)             # зелен обод
cv2.circle(slika, (100, 100), 15, (255, 0, 0), -1)            # плав, попуњен
cv2.rectangle(slika, (20, 20), (180, 180), (0, 255, 255), 2)  # жут
cv2.putText(slika, "OpenCV", (20, 240),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)`,
      },
      { type: 'h', text: 'Претварање боја' },
      {
        type: 'code',
        lang: 'python',
        code: `siva = cv2.cvtColor(slika, cv2.COLOR_BGR2GRAY)   # један канал: облик (h, w)
rgb  = cv2.cvtColor(slika, cv2.COLOR_BGR2RGB)    # за MediaPipe
hsv  = cv2.cvtColor(slika, cv2.COLOR_BGR2HSV)    # нијанса, засићење, вредност
ogledalo = cv2.flip(slika, 1)                    # 1 = лево-десно
manja = cv2.resize(slika, None, fx=0.5, fy=0.5)`,
      },
      { type: 'p', text: 'MediaPipe очекује RGB, па примери пре обраде раде cv2.cvtColor(frame, cv2.COLOR_BGR2RGB). Када је боја „промашена", прво провери то претварање.' },
      { type: 'h', text: 'Најмања петља са камером' },
      {
        type: 'shema',
        kind: 'tok',
        naslov: 'Једна итерација петље',
        caption: 'Свака игра из лекција је ова петља, само са више посла између „обради" и „прикажи".',
        pipeline: [
          { icon: '📷', title: 'Узми кадар', detail: 'read() или capture_array()' },
          { icon: '🪞', title: 'flip', detail: 'ефекат огледала' },
          { icon: '🧠', title: 'Обради и нацртај', detail: 'AI, линије, текст' },
          { icon: '🖼️', title: 'imshow', detail: 'прикажи кадар' },
          { icon: '⌨️', title: 'waitKey(1)', detail: 'тастер [q] прекида' },
        ],
      },
      {
        type: 'code',
        lang: 'python',
        code: `cap = cv2.VideoCapture(0)
while True:
    ok, kadar = cap.read()
    if not ok:
        break
    kadar = cv2.flip(kadar, 1)
    cv2.imshow("Kamera", kadar)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break
cap.release()
cv2.destroyAllWindows()`,
      },
      {
        type: 'callout',
        tone: 'info',
        title: 'Зашто waitKey(1)?',
        text: 'Без њега прозор се не освежава. waitKey даје OpenCV-у времена да нацрта слику и чита тастер; & 0xFF оставља само последњи бајт, а ord("q") је код слова q (27 је ESC).',
      },
      { type: 'p', text: 'Камера на Pi-ју ради преко Picamera2 (као у лекцији 1), па наш пример користи Picamera2 ако постоји, иначе VideoCapture. На лаптопу са USB камером ради одмах.' },
      { type: 'h', text: 'Вежба' },
      {
        type: 'steps',
        items: [
          'Покрени python opencv_slika.py. Додај још један круг и пореди сиву и HSV верзију.',
          'Покрени python opencv_slika.py --snimi ако радиш преко SSH-а без екрана, па отвори izlaz.png.',
          'Покрени python opencv_kamera.py и притисни [q]. Шта се дешава ако уклониш cv2.flip?',
          'Додај у opencv_kamera.py cv2.rectangle у средину кадра и cv2.putText са текстом „Zdravo".',
        ],
      },
    ],
  },
]
