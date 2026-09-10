import { Link } from 'react-router-dom'
import BrandMark from './BrandMark'

export default function Footer() {
  return (
    <footer className="footer">
      <div className="wrap">
        <div className="footer__grid">
          <div className="footer__brand">
            <span className="nav__brand" style={{ fontSize: 18 }}>
              <BrandMark size={24} />
              <span className="nav__brand-text">
                <span>Edge AI <b style={{ color: 'var(--accent)' }}>Пирот</b></span>
                <span className="nav__brand-tag">Наука у петој брзини</span>
              </span>
            </span>
            <p>
              „Edge AI: Наука у петој брзини“ — вештачка интелигенција на самом
              уређају, без облака. Програм радионица Техничке школе Пирот.
            </p>
          </div>
          <div className="footer__col">
            <h4>Садржај</h4>
            <Link to="/projekti">Пројекти</Link>
            <Link to="/uputstva">Упутства</Link>
            <Link to="/o-programu">О програму</Link>
          </div>
          <div className="footer__col">
            <h4>Спољно</h4>
            <a href="https://github.com/tspirot/edgeai" target="_blank" rel="noreferrer">
              GitHub · tspirot/edgeai
            </a>
            <a href="https://tsp.edu.rs" target="_blank" rel="noreferrer">
              tsp.edu.rs
            </a>
          </div>
        </div>
        <div className="footer__legal">
          © {new Date().getFullYear()} Техничка школа Пирот · edgeai.tsp.edu.rs ·
          Садржај под лиценцом CC BY-SA 4.0, кôд под MIT лиценцом.
        </div>
      </div>
    </footer>
  )
}
