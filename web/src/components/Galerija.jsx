import Figure from './Figure'

/* Две до три слике у реду — за кораке монтаже и упоредне снимке.
   На уским екранима прелази у једну колону (index.css). */

export default function Galerija({ items, caption }) {
  if (!items?.length) return null
  return (
    <div className="galerija-wrap">
      <div className={`galerija galerija--${Math.min(items.length, 3)}`}>
        {items.map((it, i) => (
          <Figure key={i} {...it} sirina="puna" caption={it.caption} />
        ))}
      </div>
      {caption && <p className="galerija__cap">{caption}</p>}
    </div>
  )
}
