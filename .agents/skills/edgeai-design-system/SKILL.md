---
name: edgeai-design-system
description: Design system guidelines, UI/UX conventions, color contrast standards (WCAG AAA), light and dark theme architecture, 3D Hero WebGL synchronization, and mobile responsive layout for edgeai.tsp.edu.rs. Use when designing, styling, adjusting themes, or fixing contrast/readability.
---

# Edge AI Пирот — Дизајн систем и UI/UX смернице

Овај skill дефинише визуелни идентитет, палету боја за тамну и светлу тему, типографију, правила за 3D WebGL сцену и принципе прилагођавања мобилним уређајима на edgeai.tsp.edu.rs.

## 1. Палета боја и контраст (WCAG AAA)

Тема се контролише преко атрибута [data-theme=light] на <html> елементу. Тамна тема је подразумевана.
Кориснички избор се памти у localStorage ('edgeai-theme') и преноси кроз реактивни хук useTheme() из src/lib/theme.js.

### Главне варијабле (src/index.css)

| Варијабла | Тамна тема (:root) | Светла тема ([data-theme=light]) | Намена |
| :--- | :--- | :--- | :--- |
| --paper | #090E0C (дубоки обсидијан) | #F5F8F6 (чист папир) | Главна позадина сајта и 3D платна |
| --surface | #111A15 | #FFFFFF | Картице, модали, мени |
| --surface-2 | #18251F | #EAF0EC | Унутрашње картице, секције |
| --surface-3 | #22342B | #DFE8E2 | Ознаке, беџеви |
| --ink | #EDF5F0 | #0E1C15 | Примарни наслови и текст (контраст > 16:1) |
| --muted | #A1B6A9 | #485E51 | Секундарни описни текст (контраст > 6.8:1) |
| --line | #22332A | #D2DED6 | Разделне линије, оквири |
| --line-strong | #334B3E | #AEC2B5 | Истакнути оквири картица |
| --accent | #4ED8A3 (неонски минт) | #0C6146 (дубока шумска зелена) | Главни акценат и дугмад |
| --btn-primary-ink | #06110D (тамна) | #FFFFFF (бела) | **Обавезна боја текста примарног дугмета** |
| --brass | #E5B842 | #8C6500 | Хардвер ознаке и златни статус |
| --alert | #FF6B6B | #BD2A24 | Упозорења и ризици облака |

> **Критично правило контраста**: Никада не користити хардкодоване боје текста попут #06110D на елементима са позадином ar(--accent). Увек користити ar(--btn-primary-ink).

---

## 2. 3D Hero сцена (src/three/HeroScene.jsx & EdgeNetwork.jsx)

3D сцена приказује интерактивну мрежу пројеката са локалном инференцом.

- **Синхронизација са темом**: HeroScene прима 	heme prop ('dark' или 'light').
- Позадина платна <color attach=background args={[bgCol]} key={bgCol} /> и магла <fog> се мењају у складу са темом:
  - Тамна: #090E0C
  - Светла: #F5F8F6
- **Чворови**:
  - Тамна: боја #0f2a22 са емисијом боје пројекта.
  - Светла: кристално бела #FFFFFF са емисијом боје пројекта.
- **Ознаке чворова**: Користе ar(--surface) и ackdrop-filter: blur(6px) тако да су читљиве преко кретања мреже.

---

## 3. Распоред за мобилне уређаје (@media (max-width: 820px))

На уским екранима:
1. **3D Анимација је на врху**:
   - Постављена у засебну фазу .hero__stage висине 350px.
   - Мрежа је центрирана на x = 0 (уместо десктоп померања од +1.15).
   - Камера је подешена са ov: 46 и z: 11.2 тако да се **цела анимација види без сечења**.
   - На дну 3D платна стоји натпис: додирни чвор за пројекат.
2. **Текст је испод анимације**:
   - .hero__inner има order: 2 и чисту позадину ar(--paper).
   - Текст не преклапа 3D чворове нити губи читљивост.
   - Дугмад су пуне ширине за лак додир прстом.
3. **Мобилни мени**:
   - Nav горња трака је фиксна са z-index: 60.
   - Листа линкова пада испод траке (	op: var(--nav-h)).

---

## 4. Специјализоване интерактивне компоненте

- EdgeVsCloud (src/components/EdgeVsCloud.jsx): Поређење латенције, приватности и протока.
- ProjectTelemetry (src/components/ProjectTelemetry.jsx): Лајв метрика (RAM, FPS, вати, модел).
- DataPipeline (src/components/DataPipeline.jsx): Интерактивни дијаграм тока података од сензора до излаза.
- CaptionSimulator (src/components/CaptionSimulator.jsx): Симулатор титлова уживо са одвојеним потврђеним речима.
- ProgramTimeline (src/components/ProgramTimeline.jsx): Временска линија фаза програма са статусима.
