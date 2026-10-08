import { Link } from 'react-router-dom'
import Seo from '../components/Seo'
import { primeri, getLekcija, lekcijeGrupe, oznaka } from '../data/lms'

function LekcijaKartica({ l }) {
  return (
    <Link to={`/lms/${l.slug}`} className="card">
      <span className="card__arrow" aria-hidden="true">↗</span>
      <span className="card__idx">{oznaka(l)}</span>
      <span className="card__title">{l.naziv}</span>
      <p className="card__text">{l.kratko}</p>
      <span className="card__meta">
        <span className="tag">{l.nivo}</span>
        <span className="tag">{l.vreme}</span>
        {l.primeri.length > 0 && <span className="tag tag--hw">{l.primeri.length} вежби</span>}
        {l.preduslov && <span className="tag">након: {getLekcija(l.preduslov)?.naziv}</span>}
      </span>
    </Link>
  )
}

export default function Lms() {
  const uvod = lekcijeGrupe('uvod')
  const redom = lekcijeGrupe('glavna')
  const bezLekcije = primeri.filter((p) => p.lekcije.length === 0)

  return (
    <>
      <Seo title="Учионица" description="Лекције и једноставни примери за Raspberry Pi 5: камера, препознавање руку, игре покретом, чет-бот без облака." />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs"><Link to="/">Почетна</Link><span>/</span><span>Учионица</span></div>
          <h1>Учионица</h1>
          <p>Лекције иду редом. Свака се завршава вежбом: примером који покренеш на Raspberry Pi-ју и мало преправиш.</p>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap">
          <h2>Предзнање</h2>
          <p>
            Ако ти је Python, NumPy, OpenCV или рад на Pi-ју нов, прођи ово прво. Ако већ знаш, слободно
            прескочи и крени од лекције 1.
          </p>
          <div className="grid grid--2">
            {uvod.map((l) => <LekcijaKartica key={l.slug} l={l} />)}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <h2>Лекције</h2>
          <div className="grid grid--2">
            {redom.map((l) => <LekcijaKartica key={l.slug} l={l} />)}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <h2>Примери</h2>
          <p>
            Све апликације из <b>lms/primeri</b>.
            {bezLekcije.length > 0 && ` ${bezLekcije.length} од њих још нема лекцију — ту су за радозналост.`}
          </p>
          <div className="grid grid--3">
            {primeri.map((p) => (
              <Link key={p.slug} to={`/lms/primeri/${p.slug}`} className="card">
                <span className="card__arrow" aria-hidden="true">↗</span>
                <span className="card__title">{p.naziv}</span>
                <p className="card__text">{p.kratko}</p>
                <span className="card__meta">
                  <span className="tag">{p.nivo}</span>
                  {p.lekcije.length === 0 && <span className="tag">лекција стиже</span>}
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
