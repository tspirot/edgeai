import { Link } from 'react-router-dom'

export default function ProjectCard({ p }) {
  return (
    <Link to={`/projekti/${p.slug}`} className="card">
      <span className="card__arrow" aria-hidden="true">↗</span>
      <span className="card__idx">{p.broj}</span>
      <span className="card__title">{p.naziv}</span>
      <p className="card__text">{p.kratko}</p>
      <span className="card__meta">
        <span className="tag tag--status">{p.status}</span>
        {p.hardver.slice(0, 2).map((h) => (
          <span key={h} className="tag tag--hw">{h}</span>
        ))}
      </span>
    </Link>
  )
}
