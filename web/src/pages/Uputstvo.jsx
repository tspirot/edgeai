import { Link, useParams } from 'react-router-dom'
import Seo from '../components/Seo'
import Content from '../components/Content'
import Readme from '../components/Readme'
import { getUputstvo, uputstva } from '../data/uputstva'
import { projekti } from '../data/projekti'
import { getReadme } from '../data/readme'
import NotFound from './NotFound'

export default function Uputstvo() {
  const { slug } = useParams()
  const u = getUputstvo(slug)
  if (!u) return <NotFound />
  const ostala = uputstva.filter((x) => x.slug !== slug).slice(0, 4)
  const vezaniProjekti = projekti
    .filter((p) => p.uputstvo === slug)
    .map((p) => ({ ...p, readme: getReadme(p.slug) }))
    .filter((p) => p.readme)

  return (
    <>
      <Seo title={u.naziv} description={u.kratko} />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs">
            <Link to="/">Почетна</Link><span>/</span>
            <Link to="/uputstva">Упутства</Link><span>/</span>
            <span>{u.naziv}</span>
          </div>
          <h1>{u.naziv}</h1>
          <p>{u.kratko}</p>
          <div className="card__meta">
            <span className="tag">{u.nivo}</span>
            <span className="tag">{u.vreme}</span>
          </div>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap layout-two">
          <div>
            <Content blocks={u.sadrzaj} />
            {vezaniProjekti.map((p) => (
              <div key={p.slug} className="readme-blok">
                <p className="kicker">
                  README пројекта · {p.ikona} {p.naziv}
                </p>
                <Readme markdown={p.readme} />
              </div>
            ))}
          </div>
          <aside className="aside">
            <h4>Друга упутства</h4>
            <ul>
              {ostala.map((x) => (
                <li key={x.slug}><Link to={`/uputstva/${x.slug}`}>{x.naziv}</Link></li>
              ))}
            </ul>
          </aside>
        </div>
      </section>
    </>
  )
}
