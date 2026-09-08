import { Link } from 'react-router-dom'
import Seo from '../components/Seo'

export default function NotFound() {
  return (
    <>
      <Seo title="Страна није пронађена" />
      <section className="section" style={{ paddingTop: 'calc(var(--nav-h) + 80px)', borderTop: 'none' }}>
        <div className="wrap wrap--narrow center">
          <p className="kicker">404</p>
          <h2>Ове стране нема</h2>
          <p style={{ color: 'var(--muted)' }}>
            Могуће да је премештена или да линк није тачан.
          </p>
          <p className="mt-40">
            <Link to="/" className="btn btn--primary">На почетну</Link>
          </p>
        </div>
      </section>
    </>
  )
}
