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
(`tone:'info'|'warn'|'alert'`, `title`, `text`), `specs`, `quote`, `shema`,
`figure`, `galerija`.

Смернице за садржај:
- Почни `{type:'p', lead:true}` — шта и зашто, 1–2 реченице.
- `steps` за редослед радњи; `code` за тачне команде (не парафразирај).
- Бар један `callout` са замком коју ученици обично упадну.
- Заврши провером („како знам да ради“).

## Графика — свако упутство мора имати бар једну схему

Схеме се цртају кодом (`web/src/components/sheme/`), прате тему светло/тамно и
не траже никакав фајл. Не описуј речима оно што се може нацртати.

```js
{ type: 'shema', kind: 'hardver', naslov: 'Шема повезивања',
  caption: 'Зашто баш овако — једна реченица.',
  data: { ploca: 'Raspberry Pi 5', veze: [
    { port: 'CSI', ikona: '📷', naziv: 'Camera Module 3', detalj: 'Full HD' },
  ] } }
```

| `kind` | Кад се користи |
| :--- | :--- |
| `hardver` | **обавезно** за свако упутство које нешто повезује или монтира |
| `scena` | кад је важно где сензор физички стоји и шта види (поглед одозго) |
| `tok` | кад се објашњава ланац обраде — прими `pipeline:[{icon,title,detail}]` |
| `kuciste` | израда кућишта: „прст“ спојеви и отвори за портове |
| `tackeShake` | 21 тачка шаке |

Пун опис поља: skill `novi-projekat`, корак 4.

**Порт је оно што ученик тражи на плочи.** Пиши стварну ознаку (`PCIe`, `CSI`,
`I²C`, `GPIO`, `USB-C`), јер је најчешћа грешка при монтажи да се кабл тражи на
погрешном прикључку — схема ту грешку спречава боље од пасуса текста.

Фотографије и видео (`figure`) само кад фајл заиста постоји у
`web/public/slike/uputstva/<slug>/` — види `web/public/slike/README.md`.

Повежи упутство са пројектом: у `projekti.js` постави `uputstvo: '<slug>'`. Тиме се
`README.md` тог пројекта аутоматски приказује на дну стране упутства.

Провера: `cd web && npm run dev` → `/uputstva` и `/uputstva/<slug>`. Погледај у
**обе теме** и на уској ширини (схеме прелазе у усправан распоред испод 700 px),
pa `npm run build`.
