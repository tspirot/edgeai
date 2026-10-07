import { useMemo } from 'react'
import { oboji } from '../lib/highlight'

/* Блок кода са обојеном синтаксом. Непознат језик се приказује као обичан текст.
   Боје су токени --k-* у index.css (по једна палета за сваку тему). */

export default function Kod({ code, lang }) {
  const delovi = useMemo(() => oboji(code, lang), [code, lang])
  return (
    <pre data-lang={lang || undefined}>
      <code>
        {delovi.map((d, i) => (d.t ? <span key={i} className={d.t}>{d.s}</span> : d.s))}
      </code>
    </pre>
  )
}
