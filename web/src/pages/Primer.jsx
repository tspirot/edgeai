import { Link, useParams } from 'react-router-dom'
import Seo from '../components/Seo'
import Readme from '../components/Readme'
import Kod from '../components/Kod'
import Figure from '../components/Figure'
import { getPrimer, lekcijeZaPrimer, primerRepo, oznaka } from '../data/lms'
import { getPrimerReadme } from '../data/readme'
import NotFound from './NotFound'
import { ghBlob } from '../lib/github'

export default function Primer() {
  const { slug } = useParams()
  const p = getPrimer(slug)
  if (!p) return <NotFound />

  const lekcije = lekcijeZaPrimer(p)
  const readme = getPrimerReadme(p.folder) || getPrimerReadme(slug)

  return (
    <>
      <Seo title={p.naziv} description={p.kratko} slika={p.slika} />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs">
            <Link to="/">Почетна</Link><span>/</span>
            <Link to="/lms">Учионица</Link><span>/</span>
            <span>{p.naziv}</span>
          </div>
          <h1>{p.naziv}</h1>
          <p>{p.kratko}</p>
          <div className="card__meta">
            <span className="tag">{p.nivo}</span>
            {p.hardver.map((h) => <span key={h} className="tag tag--hw">{h}</span>)}
          </div>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap layout-two">
          <div className="prose">
            {p.slika && (
              <div style={{ marginBottom: 32 }}>
                <Figure
                  src={p.slika}
                  alt={p.naziv}
                  caption={p.slikaOpis || `Приказ апликације „${p.naziv}“ уживо`}
                  sirina="puna"
                  odnos="16 / 9"
                />
              </div>
            )}

            {lekcije.length > 0 ? (
              <aside className="callout callout--info">
                <strong>Научи прво</strong>
                <p>
                  {lekcije.map((l, i) => (
                    <span key={l.slug}>
                      {i > 0 && ', '}
                      <Link to={`/lms/${l.slug}`}>{oznaka(l)}: {l.naziv}</Link>
                    </span>
                  ))}
                </p>
              </aside>
            ) : (
              <aside className="callout callout--info">
                <strong>Лекција стиже</strong>
                <p>За овај пример још нема лекције. Можеш га покренути и истраживати кôд самостално.</p>
              </aside>
            )}

            <h2>Покретање</h2>
            <p>Прво активирај окружење: <code>source ~/primeri/env/bin/activate</code></p>
            <Kod code={p.pokretanje} lang="bash" />
            {p.kontrole && <p><b>Тастери:</b> {p.kontrole}</p>}
            <p>
              <a href={primerRepo(p)} target="_blank" rel="noreferrer">Изворни кôд ↗</a>
              {' '}({p.folder}/{p.fajl})
              {' · '}
              <a href={ghBlob(`lms/primeri/${p.folder}/${p.fajl}`)} target="_blank" rel="noreferrer">датотека ↗</a>
              {' · '}
              <a href={ghBlob('lms/primeri/requirements.txt')} target="_blank" rel="noreferrer">requirements.txt ↗</a>
            </p>

            {readme && (
              <div className="readme-blok">
                <p className="kicker">README примера</p>
                <Readme markdown={readme} />
              </div>
            )}
          </div>
          <aside className="aside">
            <h4>Учионица</h4>
            <ul>
              <li><Link to="/lms">← Све лекције и примери</Link></li>
            </ul>
          </aside>
        </div>
      </section>
    </>
  )
}
