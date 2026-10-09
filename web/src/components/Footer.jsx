import { Link } from 'react-router-dom'
import BrandMark from './BrandMark'
import { GH_REPO, ghTree, ghBlob } from '../lib/github'

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
            <Link to="/lms">Учионица</Link>
            <Link to="/o-programu">О програму</Link>
          </div>
          <div className="footer__col">
            <h4>Спољно</h4>
            <a href={GH_REPO} target="_blank" rel="noreferrer">
              GitHub · tspirot/edgeai
            </a>
            <a href={ghTree('lms/primeri')} target="_blank" rel="noreferrer">
              Примери за Pi (lms/primeri)
            </a>
            <a href={ghTree('projekti')} target="_blank" rel="noreferrer">
              Изворни кôд пројеката
            </a>
            <a href="https://tsp.edu.rs" target="_blank" rel="noreferrer">
              tsp.edu.rs
            </a>
          </div>
        </div>
        <div className="footer__legal">
          © {new Date().getFullYear()} Техничка школа Пирот · edgeai.tsp.edu.rs ·
          Садржај под лиценцом{' '}
          <a href={ghBlob('LICENSE-CONTENT')} target="_blank" rel="noreferrer">CC BY-SA 4.0</a>, кôд под{' '}
          <a href={ghBlob('LICENSE')} target="_blank" rel="noreferrer">MIT</a> лиценцом.
        </div>
      </div>
    </footer>
  )
}
