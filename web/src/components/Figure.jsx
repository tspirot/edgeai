import { useState } from 'react'
import { useTheme } from '../lib/theme'
import { useReducedMotion } from '../lib/hooks'

/* Једина тачка кроз коју бинарни медиј улази на сајт.
   - .mp4/.webm иде као <video>, не као <img> — видео је ~10× мањи од GIF-а
     за исти садржај.
   - `srcDark` је опциона варијанта слике за тамну тему.
   - Ако фајл недостаје, приказује се уредан плејсхолдер уместо покварене слике. */

const VIDEO = /\.(mp4|webm)$/i
const ANIM = /\.gif$/i

export default function Figure({
  src,
  srcDark,
  alt,
  caption,
  poster,
  sirina = 'uska',
  odnos = '16 / 9',
}) {
  const tema = useTheme()
  const mirno = useReducedMotion()
  const [greska, setGreska] = useState(false)
  const [pusti, setPusti] = useState(false)

  if (import.meta.env.DEV && !alt) {
    console.warn(`Figure: недостаје alt за „${src}“ — обавезан је за читаче екрана.`)
  }

  const izvor = tema === 'dark' && srcDark ? srcDark : src
  const jeVideo = VIDEO.test(izvor)
  const jeGif = ANIM.test(izvor)
  // Под „смањено кретање“ анимирани медиј чека на клик корисника.
  const cekaKlik = mirno && (jeVideo || jeGif) && !pusti

  return (
    <figure className={`figure figure--${sirina}`}>
      <div className="figure__media" style={{ aspectRatio: odnos }}>
        {greska ? (
          <div className="figure__nema">
            <span aria-hidden="true">🖼️</span>
            <p>{alt || 'Слика још није додата.'}</p>
          </div>
        ) : cekaKlik ? (
          <button type="button" className="figure__pusti" onClick={() => setPusti(true)}>
            {poster && <img src={poster} alt="" loading="lazy" decoding="async" />}
            <span className="figure__pusti-znak" aria-hidden="true">▶</span>
            <span className="figure__pusti-txt">Пусти анимацију — {alt}</span>
          </button>
        ) : jeVideo ? (
          <video
            src={izvor}
            poster={poster}
            autoPlay={!mirno}
            controls={mirno}
            loop
            muted
            playsInline
            preload="metadata"
            aria-label={alt}
            onError={() => setGreska(true)}
          />
        ) : (
          <img
            src={izvor}
            alt={alt || ''}
            loading="lazy"
            decoding="async"
            onError={() => setGreska(true)}
          />
        )}
      </div>
      {caption && <figcaption className="figure__cap">{caption}</figcaption>}
    </figure>
  )
}
