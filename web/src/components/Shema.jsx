import * as sheme from './sheme'

/* Оквир око кодиране SVG схеме: наслов, платно и опис испод.
   Схема се бира преко `kind`; непознат кључ се тихо прескаче (као и остали
   непознати блокови у Content.jsx). */

export default function Shema({ kind, data, pipeline, boja, naslov, caption }) {
  const Crtez = sheme[kind]
  if (!Crtez) return null
  // Упутства немају боју пројекта — тада се користи акценат теме.
  const akcenat = boja || 'var(--accent)'

  return (
    <figure className="shema">
      {naslov && <figcaption className="shema__naslov">{naslov}</figcaption>}
      <div className="shema__platno">
        <Crtez data={data} pipeline={pipeline} boja={akcenat} />
      </div>
      {caption && <figcaption className="shema__opis">{caption}</figcaption>}
    </figure>
  )
}
