import { Link } from 'react-router-dom'

/** Приказ када WebGL није доступан или је укључено „смањено кретање“. */
export default function HeroFallback({ projekti }) {
  return (
    <div className="hero-fallback" aria-hidden="true">
      <div className="hero-fallback__nodes">
        {projekti.map((p) => (
          <Link key={p.slug} to={`/projekti/${p.slug}`} className="hero-fallback__node">
            <b>{p.broj}</b> {p.naziv}
          </Link>
        ))}
      </div>
    </div>
  )
}
