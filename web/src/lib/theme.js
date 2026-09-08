// Тамна тема је подразумевана. Избор корисника се памти у localStorage.
const KEY = 'edgeai-theme'

export function initTheme() {
  let saved = null
  try { saved = localStorage.getItem(KEY) } catch { /* приватни режим */ }
  const theme = saved === 'light' || saved === 'dark' ? saved : 'dark'
  document.documentElement.setAttribute('data-theme', theme)
}

export function getTheme() {
  return document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark'
}

export function toggleTheme() {
  const next = getTheme() === 'light' ? 'dark' : 'light'
  document.documentElement.setAttribute('data-theme', next)
  try { localStorage.setItem(KEY, next) } catch { /* игнориши */ }
  return next
}
