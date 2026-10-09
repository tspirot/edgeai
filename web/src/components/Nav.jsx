import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import BrandMark from './BrandMark'
import { useTheme, toggleTheme } from '../lib/theme'
import { GH_REPO } from '../lib/github'

const LINKS = [
  { to: '/projekti', label: 'Пројекти' },
  { to: '/uputstva', label: 'Упутства' },
  { to: '/lms', label: 'Учионица' },
  { to: '/o-programu', label: 'О програму' },
]

export default function Nav() {
  const { pathname } = useLocation()
  const isHome = pathname === '/'
  const [solid, setSolid] = useState(!isHome)
  const [open, setOpen] = useState(false)
  const theme = useTheme()

  useEffect(() => {
    if (!isHome) { setSolid(true); return }
    const onScroll = () => setSolid(window.scrollY > 40)
    onScroll()
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [isHome])

  useEffect(() => { setOpen(false) }, [pathname])

  return (
    <header className={`nav${solid || open ? ' nav--solid' : ''}${open ? ' nav--open' : ''}`}>
      <nav className="nav__inner wrap" aria-label="Главна навигација">
        <NavLink to="/" className="nav__brand">
          <BrandMark />
          <span className="nav__brand-text">
            <span>Edge AI <b>Пирот</b></span>
            <span className="nav__brand-tag">Наука у петој брзини</span>
          </span>
        </NavLink>
        <div className="nav__status-pill" title="Систем ради локално без облака">
          <span className="nav__status-pulse" />
          <span>офлајн систем</span>
        </div>
        <div className="nav__spacer" />
        
        <div className={`nav__links${open ? ' is-open' : ''}`}>
          {LINKS.map((l) => (
            <NavLink
              key={l.to}
              to={l.to}
              className={({ isActive }) => `nav__link${isActive ? ' is-active' : ''}`}
              onClick={() => setOpen(false)}
            >
              {l.label}
            </NavLink>
          ))}
        </div>

        <a
          className="nav__toggle"
          href={GH_REPO}
          target="_blank"
          rel="noreferrer"
          aria-label="Изворни кôд на GitHub-у (отвара се у новом прозору)"
          title="Изворни кôд на GitHub-у"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
            <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
          </svg>
        </a>

        <button
          type="button"
          className="nav__toggle"
          onClick={toggleTheme}
          aria-label={theme === 'light' ? 'Тамна тема' : 'Светла тема'}
          title={theme === 'light' ? 'Тамна тема' : 'Светла тема'}
        >
          {theme === 'light' ? '☾' : '☀'}
        </button>

        <button
          className="nav__burger"
          aria-expanded={open}
          aria-label="Мени"
          onClick={() => setOpen((v) => !v)}
        >
          {open ? '✕' : '☰'}
        </button>
      </nav>
    </header>
  )
}
