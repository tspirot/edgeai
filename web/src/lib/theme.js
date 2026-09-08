import { useState, useEffect } from 'react'

// Светла тема је подразумевана. Избор корисника се памти у localStorage.
const KEY = 'edgeai-theme'
export const DEFAULT_THEME = 'light'

export function initTheme() {
  let saved = null
  try { saved = localStorage.getItem(KEY) } catch { /* приватни режим */ }
  const theme = saved === 'light' || saved === 'dark' ? saved : DEFAULT_THEME
  document.documentElement.setAttribute('data-theme', theme)
}

export function getTheme() {
  return document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light'
}

export function toggleTheme() {
  const next = getTheme() === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', next)
  try { localStorage.setItem(KEY, next) } catch { /* игнориши */ }
  window.dispatchEvent(new CustomEvent('theme-change', { detail: next }))
  return next
}

export function useTheme() {
  const [theme, setTheme] = useState(getTheme)

  useEffect(() => {
    const handler = (e) => setTheme(e.detail)
    window.addEventListener('theme-change', handler)
    return () => window.removeEventListener('theme-change', handler)
  }, [])

  return theme
}

