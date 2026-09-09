import { Link } from 'react-router-dom'

export default function ProjectCard({ p }) {
  return (
    <Link to={`/projekti/${p.slug}`} className="card card--project">
      <span className="card__arrow" aria-hidden="true">↗</span>
      {/* Медијска трака се приказује само ако пројекат заиста има слику —
          картице без ње остају какве су биле, без празног оквира. */}
      {p.slika && (
        <div className="card__media">
          <img src={p.slika} alt="" loading="lazy" decoding="async" />
        </div>
      )}
      <div className="card__header">
        <span className="card__idx">{p.broj}</span>
        {p.ikona && <span className="card__sensor-icon" title="Сензор / улаз">{p.ikona}</span>}
      </div>
      <span className="card__title">{p.naziv}</span>
      <p className="card__text">{p.kratko}</p>
      <span className="card__meta">
        <span className="tag tag--status">{p.status}</span>
        {p.telemetrija?.latencija && (
          <span className="tag tag--telemetry" title="Латенција">{p.telemetrija.latencija}</span>
        )}
        {p.hardver.slice(0, 2).map((h) => (
          <span key={h} className="tag tag--hw">{h}</span>
        ))}
      </span>
    </Link>
  )
}
