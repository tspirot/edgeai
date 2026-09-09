import { useIsNarrow, useReducedMotion } from '../../lib/hooks'

/* Ток сигнала од сензора до излаза, цртан SVG-ом.
   Чита постојеће поље `pipeline` из data/projekti.js — без дуплирања података.
   Тачка која путује путањом се гаси под prefers-reduced-motion. */

function prelomi(tekst, max) {
  const reci = String(tekst).split(' ')
  const redovi = []
  let red = ''
  for (const r of reci) {
    if (red && (red + ' ' + r).length > max) {
      redovi.push(red)
      red = r
    } else {
      red = red ? red + ' ' + r : r
    }
  }
  if (red) redovi.push(red)
  return redovi.slice(0, 2)
}

export default function TokShema({ pipeline, boja = 'currentColor' }) {
  const usko = useIsNarrow()
  const mirno = useReducedMotion()
  if (!pipeline?.length) return null

  const n = pipeline.length
  const opis = `Ток обраде: ${pipeline.map((s) => s.title).join(' → ')}.`

  if (usko) {
    // Усправно: корак испод корака, стрелице надоле.
    const W = 340
    const RED = 78
    const RAZMAK = 28
    const H = n * RED + (n - 1) * RAZMAK
    return (
      <svg viewBox={`0 0 ${W} ${H}`} className="shema-svg" role="img" aria-label={opis}>
        {pipeline.map((s, i) => {
          const y = i * (RED + RAZMAK)
          return (
            <g key={i}>
              {i > 0 && (
                <path d={`M${W / 2} ${y - RAZMAK} v${RAZMAK - 8} l-5 -6 m5 6 l5 -6`}
                  className="shema-veza" fill="none" />
              )}
              <rect x="0" y={y} width={W} height={RED} rx="10" className="shema-box" />
              <circle cx="34" cy={y + RED / 2} r="17" fill={boja} opacity="0.14" />
              <text x="34" y={y + RED / 2 + 7} className="shema-emoji" textAnchor="middle">{s.icon}</text>
              <text x="64" y={y + 26} className="shema-t-ink">{s.title}</text>
              {prelomi(s.detail, 30).map((l, j) => (
                <text key={j} x="64" y={y + 45 + j * 14} className="shema-t-muted">{l}</text>
              ))}
            </g>
          )
        })}
      </svg>
    )
  }

  // Водоравно: ланац корака са анимираном тачком.
  const NODE_W = 170
  const NODE_H = 124
  const GAP = 36
  const W = n * NODE_W + (n - 1) * GAP
  const H = NODE_H + 34
  const cy = NODE_H / 2
  const putanja = `M0 ${cy} H${W}`

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="shema-svg" role="img" aria-label={opis}>
      {/* спојнице испод картица */}
      {pipeline.slice(0, -1).map((_, i) => {
        const x = i * (NODE_W + GAP) + NODE_W
        return (
          <path key={i} d={`M${x} ${cy} h${GAP - 9} l-6 -5 m6 5 l-6 5`}
            className="shema-veza" fill="none" />
        )
      })}

      {pipeline.map((s, i) => {
        const x = i * (NODE_W + GAP)
        const naslov = prelomi(s.title, 17)
        const linije = prelomi(s.detail, 24)
        const yDetalj = 58 + naslov.length * 15 + 4
        return (
          <g key={i}>
            <rect x={x} y="0" width={NODE_W} height={NODE_H} rx="12" className="shema-box" />
            <circle cx={x + NODE_W / 2} cy="26" r="16" fill={boja} opacity="0.14" />
            <text x={x + NODE_W / 2} y="32" className="shema-emoji" textAnchor="middle">{s.icon}</text>
            {naslov.map((l, j) => (
              <text key={j} x={x + NODE_W / 2} y={58 + j * 15} className="shema-t-ink" textAnchor="middle">{l}</text>
            ))}
            {linije.map((l, j) => (
              <text key={j} x={x + NODE_W / 2} y={yDetalj + j * 13} className="shema-t-mini" textAnchor="middle">{l}</text>
            ))}
            <text x={x + NODE_W / 2} y={NODE_H + 22} className="shema-t-port" textAnchor="middle">
              {String(i + 1).padStart(2, '0')}
            </text>
          </g>
        )
      })}

      {!mirno && (
        <>
          <path id="tok-putanja" d={putanja} fill="none" stroke="none" />
          <circle r="4.5" fill={boja}>
            <animateMotion dur={`${Math.max(3, n * 0.8)}s`} repeatCount="indefinite" path={putanja} />
            <animate attributeName="opacity" values="0;1;1;0" dur={`${Math.max(3, n * 0.8)}s`} repeatCount="indefinite" />
          </circle>
        </>
      )}
    </svg>
  )
}
