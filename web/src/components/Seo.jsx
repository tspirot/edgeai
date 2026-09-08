import { useEffect } from 'react'

/** Поставља <title> и meta description по страни. */
export default function Seo({ title, description }) {
  useEffect(() => {
    document.title = title ? `${title} · Edge AI Пирот` : 'Edge AI Пирот'
    if (description) {
      let m = document.querySelector('meta[name="description"]')
      if (!m) {
        m = document.createElement('meta')
        m.setAttribute('name', 'description')
        document.head.appendChild(m)
      }
      m.setAttribute('content', description)
    }
  }, [title, description])
  return null
}
