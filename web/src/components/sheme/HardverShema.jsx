import { useIsNarrow } from '../../lib/hooks'

/* Шема повезивања: плоча (Pi 5 / Jetson) и периферије на означеним портовима.
   Боје долазе из CSS променљивих преко класа — схема прати тему светло/тамно.
   `boja` је акценат пројекта из data/projekti.js. */

const RED_V = 62 // висина реда периферије
const RAZMAK = 16

function Periferija({ x, y, w, veza }) {
  return (
    <g>
      <rect x={x} y={y} width={w} height={RED_V} rx="10" className="shema-box" />
      <text x={x + 22} y={y + RED_V / 2 + 7} className="shema-emoji">{veza.ikona}</text>
      <text x={x + 48} y={y + 25} className="shema-t-ink">{veza.naziv}</text>
      {veza.detalj && (
        <text x={x + 48} y={y + 43} className="shema-t-muted">{veza.detalj}</text>
      )}
    </g>
  )
}

function Ploca({ x, y, w, h, naziv, boja }) {
  const cx = x + w / 2
  return (
    <g>
      <rect x={x} y={y} width={w} height={h} rx="12" className="shema-ploca" />
      {/* чип са акцентом пројекта */}
      <rect
        x={cx - 30} y={y + h / 2 - 32} width="60" height="60" rx="8"
        fill={boja} opacity="0.16" stroke={boja} strokeWidth="1.5"
      />
      <text x={cx} y={y + h / 2 + 4} className="shema-chip-txt" textAnchor="middle">NPU</text>
      <text x={cx} y={y + h - 16} className="shema-t-ink" textAnchor="middle">{naziv}</text>
    </g>
  )
}

export default function HardverShema({ data, boja = 'currentColor' }) {
  const usko = useIsNarrow()
  if (!data?.veze?.length) return null
  const { ploca = 'Raspberry Pi 5', veze } = data
  const n = veze.length
  const opis = `Шема повезивања: ${ploca} са периферијама — ${veze
    .map((v) => `${v.naziv} на ${v.port}`)
    .join(', ')}.`

  if (usko) {
    // Усправно: плоча на врху, магистрала надоле, периферије у колони.
    const W = 340
    const plocaH = 96
    const start = plocaH + 34
    const H = start + n * (RED_V + RAZMAK)
    const busX = 26
    return (
      <svg viewBox={`0 0 ${W} ${H}`} className="shema-svg" role="img" aria-label={opis}>
        <Ploca x={70} y={0} w={200} h={plocaH} naziv={ploca} boja={boja} />
        <path d={`M170 ${plocaH} v14 H${busX} V${start + (n - 1) * (RED_V + RAZMAK) + RED_V / 2}`}
          className="shema-veza" fill="none" />
        {veze.map((v, i) => {
          const y = start + i * (RED_V + RAZMAK)
          return (
            <g key={i}>
              <path d={`M${busX} ${y + RED_V / 2} H78`} className="shema-veza" fill="none" />
              <text x={busX + 4} y={y + RED_V / 2 - 8} className="shema-t-port">{v.port}</text>
              <Periferija x={78} y={y} w={W - 78} veza={v} />
            </g>
          )
        })}
      </svg>
    )
  }

  // Водоравно: плоча лево, периферије десно, кривине између.
  const W = 760
  const H = Math.max(210, n * (RED_V + RAZMAK) + 20)
  const plocaW = 190
  const plocaH = 150
  const plocaY = (H - plocaH) / 2
  const boxX = 380
  const start = (H - (n * RED_V + (n - 1) * RAZMAK)) / 2

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="shema-svg" role="img" aria-label={opis}>
      <Ploca x={24} y={plocaY} w={plocaW} h={plocaH} naziv={ploca} boja={boja} />
      {veze.map((v, i) => {
        const y = start + i * (RED_V + RAZMAK)
        const y2 = y + RED_V / 2
        const y1 = plocaY + plocaH * ((i + 1) / (n + 1))
        const x1 = 24 + plocaW
        return (
          <g key={i}>
            <path
              d={`M${x1} ${y1} C${x1 + 80} ${y1}, ${boxX - 80} ${y2}, ${boxX} ${y2}`}
              className="shema-veza" fill="none"
            />
            <circle cx={x1} cy={y1} r="4" className="shema-port-tacka" />
            <text x={x1 + 14} y={y1 - 8} className="shema-t-port">{v.port}</text>
            <Periferija x={boxX} y={y} w={W - boxX - 8} veza={v} />
          </g>
        )
      })}
    </svg>
  )
}
