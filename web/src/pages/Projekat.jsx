import { Link, useParams } from 'react-router-dom'
import Seo from '../components/Seo'
import Content from '../components/Content'
import { getProjekat } from '../data/projekti'
import { getUputstvo } from '../data/uputstva'
import NotFound from './NotFound'

export default function Projekat() {
  const { slug } = useParams()
  const p = getProjekat(slug)
  if (!p) return <NotFound />
  const uputstvo = p.uputstvo ? getUputstvo(p.uputstvo) : null

  return (
    <>
      <Seo title={p.naziv} description={p.kratko} />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs">
            <Link to="/">Почетна</Link><span>/</span>
            <Link to="/projekti">Пројекти</Link><span>/</span>
            <span>{p.naziv}</span>
          </div>
          <h1>{p.naziv}</h1>
          <p>{p.kratko}</p>
          <div className="card__meta">
            <span className="tag tag--status">{p.status}</span>
            {p.hardver.map((h) => <span key={h} className="tag tag--hw">{h}</span>)}
          </div>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap layout-two">
          <div>
            <Content blocks={p.sadrzaj} />
          </div>
          <aside className="aside">
            <h4>Технологије</h4>
            <ul>
              {p.tehnologije?.map((t) => <li key={t}>{t}</li>)}
            </ul>
            <h4>Хардвер</h4>
            <div>
              {p.hardver.map((h) => <span key={h} className="tag tag--hw">{h}</span>)}
            </div>
            {(uputstvo || p.repo) && (
              <>
                <h4 style={{ marginTop: 24 }}>Даље</h4>
                <ul>
                  {uputstvo && <li><Link to={`/uputstva/${uputstvo.slug}`}>Упутство: {uputstvo.naziv}</Link></li>}
                  {p.repo && <li><a href={p.repo} target="_blank" rel="noreferrer">Изворни кôд ↗</a></li>}
                </ul>
              </>
            )}
          </aside>
        </div>
      </section>

      <section className="section">
        <div className="wrap center">
          <Link to="/projekti" className="btn btn--ghost">← Сви пројекти</Link>
        </div>
      </section>
    </>
  )
}
