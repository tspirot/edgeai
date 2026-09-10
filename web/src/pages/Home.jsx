import { useNavigate, Link } from 'react-router-dom'
import Seo from '../components/Seo'
import ProjectCard from '../components/ProjectCard'
import ErrorBoundary from '../components/ErrorBoundary'
import HeroScene from '../three/HeroScene'
import HeroFallback from '../three/HeroFallback'
import EdgeVsCloud from '../components/EdgeVsCloud'
import { projekti } from '../data/projekti'
import { useReducedMotion, useIsMobile } from '../lib/hooks'
import { useTheme } from '../lib/theme'

export default function Home() {
  const navigate = useNavigate()
  const reduced = useReducedMotion()
  const mobile = useIsMobile()
  const theme = useTheme()

  return (
    <>
      <Seo
        title={null}
        description="Edge AI: Наука у петој брзини — програм Техничке школе Пирот. Вештачка интелигенција која ради на самом уређају, без облака. Пројекти, упутства и радионице."
      />

      <section className="hero">
        <div className="hero__stage">
          {reduced ? (
            <HeroFallback projekti={projekti} />
          ) : (
            <ErrorBoundary fallback={<HeroFallback projekti={projekti} />}>
              <HeroScene
                projekti={projekti}
                onSelect={(slug) => navigate(`/projekti/${slug}`)}
                reduced={reduced}
                mobile={mobile}
                theme={theme}
              />
            </ErrorBoundary>
          )}
          <div className="hero__scrim" />
          <div className="hero__hint">{mobile ? 'додирни чвор за пројекат' : 'кликни на чвор'}</div>
        </div>

        <div className="hero__inner">
          <span className="hero__badge"><i />локална инференца · без облака</span>
          <p className="hero__slogan">Edge AI: <em>Наука у петој брзини</em></p>
          <h1>Вештачка интелигенција која ради <em>на самом уређају</em></h1>
          <p className="hero__dek">
            Програм радионица Техничке школе Пирот. Ученици праве уређаје који
            гледају, слушају и одлучују — а да ниједан податак не оде на туђи
            сервер.
          </p>
          <div className="hero__cta">
            <Link to="/projekti" className="btn btn--primary">Погледај пројекте →</Link>
            <Link to="/o-programu" className="btn btn--ghost">О програму</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <div className="section__head">
            <p className="kicker">Зашто „edge“</p>
            <h2>Облак није неопходан. Овде је доказ.</h2>
            <p>
              Иста ствар коју нуде велики сервиси преко интернета — препознавање
              слике и говора — ради на плочи величине длана, без мреже.
            </p>
          </div>
          
          <EdgeVsCloud />

          <div className="grid grid--4 mt-40">
            <div className="card">
              <span className="card__title">Приватност</span>
              <p className="card__text">Слика и звук се обрађују локално и нигде се не шаљу нити снимају.</p>
            </div>
            <div className="card">
              <span className="card__title">Без кашњења</span>
              <p className="card__text">Нема пута до сервера и назад — резултат стиже одмах.</p>
            </div>
            <div className="card">
              <span className="card__title">Ради без интернета</span>
              <p className="card__text">На терену, у сали, на пешачком прелазу код школе.</p>
            </div>
            <div className="card">
              <span className="card__title">Јефтино у раду</span>
              <p className="card__text">Нема претплате ни трошка по упиту — само струја.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="wrap">
          <div className="section__head">
            <p className="kicker">Пројекти</p>
            <h2>Пет прототипова, свака група води један</h2>
            <p>Од идеје до демоа на Demo Day-у. Сваки ради офлајн и везан је за Пирот.</p>
          </div>
          <div className="grid grid--3">
            {projekti.map((p) => <ProjectCard key={p.slug} p={p} />)}
            <Link to="/o-programu" className="card">
              <span className="card__arrow" aria-hidden="true">↗</span>
              <span className="card__idx">06</span>
              <span className="card__title">Како програм тече</span>
              <p className="card__text">Четири активности — од опреме и курикулума до радионица и Demo Day-а.</p>
            </Link>
          </div>
          <p className="center mt-40">
            <Link to="/projekti" className="btn btn--ghost">Све о пројектима →</Link>
          </p>
        </div>
      </section>

      <section className="section">
        <div className="wrap wrap--narrow center">
          <p className="kicker">Демонстрација</p>
          <h2>Титлови уживо, без облака</h2>
          <p style={{ color: 'var(--muted)', fontSize: 18 }}>
            Наш најјачи демо: препознавање говора на српском које ради на
            Raspberry Pi-ју и исписује титлове у реалном времену — за ученике
            оштећеног слуха. Звук никад не напушта учионицу.
          </p>
          <p className="mt-40">
            <Link to="/projekti/titlovi-uzivo" className="btn btn--primary">Како то ради →</Link>
          </p>
        </div>
      </section>
    </>
  )
}
