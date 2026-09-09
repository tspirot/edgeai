import { useEffect } from 'react'

const SAJT = 'https://edgeai.tsp.edu.rs'
const PODRAZUMEVANA_SLIKA = `${SAJT}/slike/share/edgeai-share.png`

/** Поставља или мења meta таг, правећи га ако не постоји. */
function meta(kljuc, vrednost, atribut = 'name') {
  if (!vrednost) return
  let m = document.head.querySelector(`meta[${atribut}="${kljuc}"]`)
  if (!m) {
    m = document.createElement('meta')
    m.setAttribute(atribut, kljuc)
    document.head.appendChild(m)
  }
  m.setAttribute('content', vrednost)
}

/** Наслов, опис и слика за дељење — по страни.
    `slika` је путања од корена (нпр. /slike/titlovi-uzivo/hero.png);
    ако се не наведе, користи се заједничка картица програма. */
export default function Seo({ title, description, slika }) {
  useEffect(() => {
    const pun = title ? `${title} · Edge AI Пирот` : 'Edge AI Пирот'
    document.title = pun

    meta('description', description)
    meta('og:title', pun, 'property')
    meta('og:description', description, 'property')
    meta('og:url', SAJT + window.location.pathname, 'property')
    meta('og:image', slika ? SAJT + slika : PODRAZUMEVANA_SLIKA, 'property')
  }, [title, description, slika])

  return null
}
