import { useState } from 'react'
import { Link } from 'react-router-dom'
import Seo from '../components/Seo'
import { primeri, getLekcija, lekcijeGrupe, oznaka } from '../data/lms'
import { ghTree, ghBlob } from '../lib/github'

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
  const [filter, setFilter] = useState('sve')
  const uvod = lekcijeGrupe('uvod')
  const redom = lekcijeGrupe('glavna')
  const bezLekcije = primeri.filter((p) => p.lekcije.length === 0)

  const filtriraniPrimeri = primeri.filter((p) => {
    if (filter === 'set37') return p.hardver?.some((h) => h.includes('37 у 1'))
    if (filter === 'kamera') return !p.hardver?.some((h) => h.includes('37 у 1'))
    return true
  })

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
            Све апликације из <a href={ghTree('lms/primeri')} target="_blank" rel="noreferrer"><b>lms/primeri</b> ↗</a>
            (зависности: <a href={ghBlob('lms/primeri/requirements.txt')} target="_blank" rel="noreferrer">requirements.txt ↗</a>).
            {bezLekcije.length > 0 && ` ${bezLekcije.length} од њих још нема лекцију — ту су за радозналост.`}
          </p>

          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', margin: '16px 0 24px' }}>
            <button
              type="button"
              className={`btn btn--sm ${filter === 'sve' ? 'btn--primary' : 'btn--ghost'}`}
              onClick={() => setFilter('sve')}
            >
              Сви примери ({primeri.length})
            </button>
            <button
              type="button"
              className={`btn btn--sm ${filter === 'set37' ? 'btn--primary' : 'btn--ghost'}`}
              onClick={() => setFilter('set37')}
            >
              🔌 Сет 37 у 1 ({primeri.filter((p) => p.hardver?.some((h) => h.includes('37 у 1'))).length})
            </button>
            <button
              type="button"
              className={`btn btn--sm ${filter === 'kamera' ? 'btn--primary' : 'btn--ghost'}`}
              onClick={() => setFilter('kamera')}
            >
              📷 Само камера ({primeri.filter((p) => !p.hardver?.some((h) => h.includes('37 у 1'))).length})
            </button>
          </div>

          <div className="grid grid--3">
            {filtriraniPrimeri.map((p) => (
              <Link key={p.slug} to={`/lms/primeri/${p.slug}`} className="card">
                <span className="card__arrow" aria-hidden="true">↗</span>
                <span className="card__title">{p.naziv}</span>
                <p className="card__text">{p.kratko}</p>
                <span className="card__meta">
                  <span className="tag">{p.nivo}</span>
                  {p.hardver?.some((h) => h.includes('37 у 1')) && (
                    <span className="tag tag--hw">🔌 Сет 37 у 1</span>
                  )}
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
