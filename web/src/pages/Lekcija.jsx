import { Link, useParams } from 'react-router-dom'
import Seo from '../components/Seo'
import Content from '../components/Content'
import Kviz from '../components/Kviz'
import ProjectCard from '../components/ProjectCard'
import { projekti } from '../data/projekti'
import { lekcije, getLekcija, primeriLekcije } from '../data/lms'
import NotFound from './NotFound'

export default function Lekcija() {
  const { slug } = useParams()
  const l = getLekcija(slug)
  if (!l) return <NotFound />

  const redom = [...lekcije].sort((a, b) => a.redosled - b.redosled)
  const i = redom.findIndex((x) => x.slug === slug)
  const prethodna = redom[i - 1]
  const sledeca = redom[i + 1]
  const preduslov = l.preduslov ? getLekcija(l.preduslov) : null
  const vezbe = primeriLekcije(l)
  const vezaniProjekti = (l.projekti || []).map((s) => projekti.find((p) => p.slug === s)).filter(Boolean)

  return (
    <>
      <Seo title={l.naziv} description={l.kratko} />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs">
            <Link to="/">Почетна</Link><span>/</span>
            <Link to="/lms">Учионица</Link><span>/</span>
            <span>{l.naziv}</span>
          </div>
          <h1>{l.naziv}</h1>
          <p>{l.kratko}</p>
          <div className="card__meta">
            <span className="tag">Лекција {l.redosled}</span>
            <span className="tag">{l.nivo}</span>
            <span className="tag">{l.vreme}</span>
          </div>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap layout-two">
          <div>
            {preduslov && (
              <aside className="callout callout--info">
                <strong>Прво прођи</strong>
                <p><Link to={`/lms/${preduslov.slug}`}>{preduslov.naziv}</Link></p>
              </aside>
            )}
            <Content
              blocks={[
                { type: 'h', text: 'Након лекције умећеш да…' },
                { type: 'ul', items: l.ishodi },
                ...l.sadrzaj,
              ]}
            />

            {vezbe.length > 0 && (
              <>
                <h2>Вежба: покрени пример</h2>
                <div className="grid grid--2">
                  {vezbe.map((p) => (
                    <Link key={p.slug} to={`/lms/primeri/${p.slug}`} className="card">
                      <span className="card__arrow" aria-hidden="true">↗</span>
                      <span className="card__title">{p.naziv}</span>
                      <p className="card__text">{p.kratko}</p>
                      <span className="card__meta">
                        <span className="tag">{p.nivo}</span>
                      </span>
                    </Link>
                  ))}
                </div>
              </>
            )}

            {vezaniProjekti.length > 0 && (
              <>
                <h2>Следећи корак: пројекти</h2>
                <div className="grid grid--2">
                  {vezaniProjekti.map((p) => <ProjectCard key={p.slug} p={p} />)}
                </div>
              </>
            )}

            <Kviz key={l.slug} id={l.slug} pitanja={l.kviz} />

            <nav className="card__meta" aria-label="Лекције" style={{ marginTop: 40, justifyContent: 'space-between' }}>
              {prethodna ? <Link to={`/lms/${prethodna.slug}`} className="tag">← {prethodna.naziv}</Link> : <span />}
              {sledeca ? <Link to={`/lms/${sledeca.slug}`} className="tag">{sledeca.naziv} →</Link> : <span />}
            </nav>
          </div>
          <aside className="aside">
            <h4>Све лекције</h4>
            <ul>
              {redom.map((x) => (
                <li key={x.slug}>
                  <Link to={`/lms/${x.slug}`}>{x.redosled}. {x.naziv}</Link>
                </li>
              ))}
            </ul>
          </aside>
        </div>
      </section>
    </>
  )
}
