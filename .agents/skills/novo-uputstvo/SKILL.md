---
name: novo-uputstvo
description: Add a new guide/tutorial to the Edge AI site (uputstva section). Use when asked to add or write a new uputstvo, radna lista, or how-to page.
---

# Ново упутство

Свако упутство је један унос у `web/src/data/uputstva.js`. Страна и картица се
генеришу — нема ручних рута.

```js
{
  slug: 'kratko-ime',          // /uputstva/kratko-ime
  naziv: 'Пун наслов упутства',
  kratko: 'Једна реченица за картицу.',
  nivo: 'основно',             // 'основно' | 'средње' | 'напредно'
  vreme: '40 мин',             // или 'радионица'
  sadrzaj: [ /* исти блокови као код пројеката */ ],
}
```

Блокови: `p` (`lead?`), `h`/`h3`, `ul`/`ol`/`steps`, `code` (`lang?`), `callout`
(`tone:'info'|'warn'|'alert'`, `title`, `text`), `specs`, `quote`.

Смернице за садржај:
- Почни `{type:'p', lead:true}` — шта и зашто, 1–2 реченице.
- `steps` за редослед радњи; `code` за тачне команде (не парафразирај).
- Бар један `callout` са замком коју ученици обично упадну.
- Заврши провером („како знам да ради“).

Повежи упутство са пројектом: у `projekti.js` постави `uputstvo: '<slug>'`.

Провера: `cd web && npm run dev` → `/uputstva` и `/uputstva/<slug>`, па `npm run build`.
