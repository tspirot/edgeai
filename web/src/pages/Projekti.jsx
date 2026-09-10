import Seo from '../components/Seo'
import ProjectCard from '../components/ProjectCard'
import { projekti, rezervneIdeje } from '../data/projekti'

export default function Projekti() {
  return (
    <>
      <Seo title="Пројекти" description="Пет прототипова програма „Edge AI: Наука у петој брзини“ — детекција објеката, класификација врста, контрола квалитета, титлови уживо и знаковна азбука." />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs"><a href="/">Почетна</a><span>/</span><span>Пројекти</span></div>
          <h1>Пројекти</h1>
          <p>Свака група води један прототип од идеје до демоа. Сви раде офлајн, сви су везани за Пирот.</p>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap">
          <div className="grid grid--3">
            {projekti.map((p) => <ProjectCard key={p.slug} p={p} />)}
            <a className="card" href="https://github.com/tspirot/edgeai" target="_blank" rel="noreferrer">
              <span className="card__arrow" aria-hidden="true">↗</span>
              <span className="card__idx">06</span>
              <span className="card__title">Имаш идеју?</span>
              <p className="card__text">Свака група може да замени свој прототип. Предлоге отвори као issue на GitHub-у.</p>
            </a>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <div className="section__head">
            <p className="kicker">Резервне идеје</p>
            <h2>Ако нека група хоће нешто друго</h2>
          </div>
          <div className="grid grid--3">
            {rezervneIdeje.map((r) => (
              <div key={r.naziv} className="card">
                <span className="card__title">{r.naziv}</span>
                <p className="card__text">{r.tekst}</p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  )
}
