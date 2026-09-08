import { useEffect, useState } from 'react'
import { NavLink, useLocation } from 'react-router-dom'
import BrandMark from './BrandMark'
import { useTheme, toggleTheme } from '../lib/theme'

const LINKS = [
  { to: '/projekti', label: 'Пројекти' },
  { to: '/uputstva', label: 'Упутства' },
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
          <span>Edge AI <b>Пирот</b></span>
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
