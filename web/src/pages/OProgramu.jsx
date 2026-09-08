import { Link } from 'react-router-dom'
import Seo from '../components/Seo'
import Content from '../components/Content'
import ProgramTimeline from '../components/ProgramTimeline'
import { program } from '../data/program'

export default function OProgramu() {
  return (
    <>
      <Seo title="О програму" description={program.dek} />
      <header className="pagehead">
        <div className="wrap">
          <div className="crumbs"><a href="/">Почетна</a><span>/</span><span>О програму</span></div>
          <h1>О програму</h1>
          <p>{program.dek}</p>
        </div>
      </header>

      <section className="section" style={{ borderTop: 'none' }}>
        <div className="wrap wrap--narrow">
          <Content blocks={program.sta} />
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <div className="section__head">
            <p className="kicker">Активности</p>
            <h2>Како програм тече</h2>
            <p>Четири фазе развоја — од хардверске опреме до отвореног Demo Day-а.</p>
          </div>
          
          <ProgramTimeline aktivnosti={program.aktivnosti} />
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <div className="section__head">
            <p className="kicker">Опрема</p>
            <h2>Лабораторија</h2>
          </div>
          <div className="prose">
            <ul>
              {program.oprema.map((o) => <li key={o}>{o}</li>)}
            </ul>
            <p>
              Кућишта се не купују — праве се на CO2 ласеру и 3D штампачу у
              школском Makers Lab-у. Монитори и тастатуре су постојећа опрема
              кабинета.
            </p>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <div className="section__head">
            <p className="kicker">Партнери</p>
            <h2>Ко учествује</h2>
          </div>
          <div className="grid grid--2">
            {program.partneri.map((p) => (
              <div key={p.naziv} className="card">
                <span className="card__title">{p.naziv}</span>
                <p className="card__text">{p.uloga}</p>
              </div>
            ))}
          </div>
          <p className="center mt-40">
            <Link to="/projekti" className="btn btn--primary">Погледај пројекте →</Link>
          </p>
        </div>
      </section>
    </>
  )
}
