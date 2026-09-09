---
name: novi-projekat
description: Add a new student project to the Edge AI site (project page, 3D hero node, optional linked guide and code folder). Use when asked to add/create a new projekat or replace an existing prototype.
---

# Нови пројекат на сајту

Сваки пројекат је један унос у `web/src/data/projekti.js`. Страна и 3D чвор на
насловној се генеришу из тог уноса — нема ручног додавања рута ни компоненти.

## Кораци

1. **Додај унос** у низ `projekti` у `web/src/data/projekti.js`:

   ```js
   {
     slug: 'kratko-ime',          // URL: /projekti/kratko-ime — латиница, без размака
     broj: '06',
     naziv: 'Пун назив пројекта',
     kratko: 'Једна реченица за картицу и SEO опис.',
     status: 'предлог',            // 'предлог' | 'у изради' | 'готово'
     boja: '#5FBA98',              // зелена #5FBA98 или мосинг #D8AE45
     cvor: 'Кратко име',           // натпис чвора у 3D сцени (2–3 речи)
     pozicija: [x, y, z],          // положај чвора — види ниже
     hardver: ['Raspberry Pi 5', '...'],
     tehnologije: ['...'],
     uputstvo: 'slug-uputstva',    // необавезно, веза ка упутству
     repo: 'https://github.com/tspirot/edgeai/tree/main/projekti/kratko-ime', // ако има кôд
     sadrzaj: [ /* блокови, види доле */ ],
   }
   ```

2. **`pozicija` чвора** (3D сцена, `web/src/three/EdgeNetwork.jsx`):
   - `x` од −1.5 до 3.5 (десна половина екрана — лева је резервисана за наслов)
   - `y` од −2 до 2
   - `z` од −2.6 до 2.4 (веће = ближе камери, крупнији чвор)
   - Провери да се натпис не поклапа са другим — покрени `npm run dev` и погледај.
   - Сцена ради за било који број чворова; линије и импулси се додају аутоматски.

3. **Блокови садржаја** (`sadrzaj`) — рендерује их `web/src/components/Content.jsx`:
   `{type:'p', text, lead?}` · `{type:'h'|'h3', text}` · `{type:'ul'|'ol'|'steps', items:[]}`
   · `{type:'code', code, lang?}` · `{type:'callout', tone:'info'|'warn'|'alert', title, text}`
   · `{type:'specs', items:[]}` · `{type:'quote', text, cite?}`

4. **Ако пројекат има кôд**: направи `projekti/<slug>/` (по узору на `titlovi-uzivo`),
   додај `repo` у унос и по потреби ново упутство (skill `novo-uputstvo`).
   `projekti/<slug>/README.md` се аутоматски рендерује на дну везаног упутства
   (`uputstvo:` слог) — увоз преко `web/src/data/readme.js`, ништа се не подешава ручно.

5. **Провера**: `cd web && npm run dev` → `/projekti`, `/projekti/<slug>`, насловна.
   Затим `npm run build` да нема грешке.

## Замена постојећег прототипа

Пријава дозвољава замену прототипа без анекса. Само измени постојећи унос
(задржи `slug` ако је страна већ дељена, иначе промени и `slug`).
