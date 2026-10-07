import { useState } from 'react'

/* Кратак квиз за самопроверу: нема чувања ни слања — резултат живи само на страни.
   „Провери“ се откључава кад су сва питања одговорена; после провере се приказују
   тачност и објашњење, а „Покушај поново“ чисти избор. */

export default function Kviz({ pitanja, id }) {
  const [izbor, setIzbor] = useState({})
  const [provereno, setProvereno] = useState(false)

  if (!pitanja?.length) return null

  const odgovoreno = pitanja.every((_, i) => izbor[i] !== undefined)
  const tacnih = pitanja.filter((p, i) => izbor[i] === p.tacno).length

  const reset = () => { setIzbor({}); setProvereno(false) }

  return (
    <section className="kviz" aria-labelledby={`${id}-kviz`}>
      <h2 id={`${id}-kviz`}>Провери знање</h2>
      {pitanja.map((p, i) => (
        <fieldset key={i} className="kviz__pitanje" disabled={provereno}>
          <legend>{i + 1}. {p.pitanje}</legend>
          {p.opcije.map((o, k) => {
            const stanje = provereno
              ? k === p.tacno ? 'is-tacno' : izbor[i] === k ? 'is-pogresno' : ''
              : ''
            return (
              <label key={k} className={`kviz__opcija ${stanje}`}>
                <input
                  type="radio"
                  name={`${id}-${i}`}
                  checked={izbor[i] === k}
                  onChange={() => setIzbor((s) => ({ ...s, [i]: k }))}
                />
                <span>{o}</span>
                {stanje === 'is-tacno' && <span className="kviz__oznaka">тачно</span>}
                {stanje === 'is-pogresno' && <span className="kviz__oznaka">твој избор</span>}
              </label>
            )
          })}
          {provereno && <p className="kviz__obj">{p.objasnjenje}</p>}
        </fieldset>
      ))}
      <div className="kviz__akcije">
        {!provereno ? (
          <button type="button" className="btn btn--primary" disabled={!odgovoreno} onClick={() => setProvereno(true)}>
            Провери
          </button>
        ) : (
          <button type="button" className="btn btn--ghost" onClick={reset}>Покушај поново</button>
        )}
        <span className="kviz__rezultat" role="status" aria-live="polite">
          {provereno
            ? `Тачно: ${tacnih} од ${pitanja.length}`
            : odgovoreno ? '' : `Одговорено: ${Object.keys(izbor).length} од ${pitanja.length}`}
        </span>
      </div>
    </section>
  )
}
