import { Link } from 'react-router-dom'
import Seo from '../components/Seo'
import { uputstva } from '../data/uputstva'

export default function Uputstva() {
  return (
    <>
      <Seo title="Упутства" description="Корак-по-корак упутства за радионице Edge AI: припрема Raspberry Pi-ја, AI HAT+ Hailo, IMX500 камера, кућишта, Demo Day." />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs"><a href="/">Почетна</a><span>/</span><span>Упутства</span></div>
          <h1>Упутства</h1>
          <p>Радне листе за радионице. Свако упутство је самостално и води од нуле до провере.</p>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap">
          <div className="grid grid--2">
            {uputstva.map((u) => (
              <Link key={u.slug} to={`/uputstva/${u.slug}`} className="card">
                <span className="card__arrow" aria-hidden="true">↗</span>
                <span className="card__title">{u.naziv}</span>
                <p className="card__text">{u.kratko}</p>
                <span className="card__meta">
                  <span className="tag">{u.nivo}</span>
                  <span className="tag">{u.vreme}</span>
                </span>
              </Link>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
