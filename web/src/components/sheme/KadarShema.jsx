/* Кадар као низ бројева: мрежа пиксела са осама (висина, ширина, канали)
   и један увећан пиксел са три вредности. Показује да слика за рачунар
   није „слика“ него матрица облика (висина, ширина, 3). */

const KOLONE = 8
const REDOVI = 6
const CELIJA = 28

// Детерминистичке „осветљености“ ћелија — исти цртеж при сваком рендеру.
const sjaj = (r, k) => 0.18 + 0.62 * Math.abs(Math.sin((r + 1) * 1.7 + (k + 1) * 0.9))

export default function KadarShema({ data = {}, boja = 'currentColor' }) {
  const { sirina = 640, visina = 480, kanali = 3, piksel = [182, 143, 97], izabran = [2, 3] } = data
  const GX = 70
  const GY = 34
  const mrezaW = KOLONE * CELIJA
  const mrezaH = REDOVI * CELIJA
  const [ir, ik] = izabran
  const px = GX + ik * CELIJA
  const py = GY + ir * CELIJA

  // Увећани пиксел десно.
  const DX = 330
  const DY = 52
  const traka = 120

  return (
    <svg
      viewBox="0 0 560 250"
      className="shema-svg"
      role="img"
      aria-label={`Кадар је матрица пиксела облика (${visina}, ${sirina}, ${kanali}). Сваки пиксел има ${kanali} броја од 0 до 255, по један за сваки канал боје.`}
    >
      {/* осе */}
      <text x={GX + mrezaW / 2} y={20} className="shema-t-ink" textAnchor="middle">ширина = {sirina}</text>
      <line x1={GX} y1={26} x2={GX + mrezaW} y2={26} className="shema-veza" />
      <text
        x={34} y={GY + mrezaH / 2}
        className="shema-t-ink" textAnchor="middle"
        transform={`rotate(-90 34 ${GY + mrezaH / 2})`}
      >
        висина = {visina}
      </text>
      <line x1={GX - 8} y1={GY} x2={GX - 8} y2={GY + mrezaH} className="shema-veza" />

      {/* мрежа пиксела */}
      {Array.from({ length: REDOVI }).map((_, r) =>
        Array.from({ length: KOLONE }).map((__, k) => (
          <rect
            key={`${r}-${k}`}
            x={GX + k * CELIJA} y={GY + r * CELIJA}
            width={CELIJA - 2} height={CELIJA - 2} rx="3"
            fill={boja} opacity={sjaj(r, k)}
          />
        )),
      )}
      <text x={GX + mrezaW / 2} y={GY + mrezaH + 22} className="shema-t-muted" textAnchor="middle">
        облик кадра: ({visina}, {sirina}, {kanali})
      </text>

      {/* изабрани пиксел и спојница ка увећању */}
      <rect x={px - 2} y={py - 2} width={CELIJA + 2} height={CELIJA + 2} rx="4"
        fill="none" stroke={boja} strokeWidth="2.5" />
      <path
        d={`M${px + CELIJA} ${py + CELIJA / 2} C ${px + 120} ${py + CELIJA / 2}, ${DX - 60} ${DY + 50}, ${DX - 14} ${DY + 50}`}
        className="shema-veza" strokeDasharray="4 4"
      />

      {/* увећани пиксел: три канала */}
      <text x={DX} y={DY - 16} className="shema-t-ink">један пиксел = {kanali} броја</text>
      {piksel.slice(0, kanali).map((v, i) => {
        const y = DY + i * 44
        return (
          <g key={i}>
            <text x={DX} y={y + 13} className="shema-t-port">канал {i}</text>
            <rect x={DX + 62} y={y} width={traka} height={18} rx="4" className="shema-box" />
            <rect x={DX + 62} y={y} width={(traka * v) / 255} height={18} rx="4" fill={boja} opacity="0.75" />
            <text x={DX + 62 + traka + 10} y={y + 14} className="shema-t-ink">{v}</text>
          </g>
        )
      })}
      <text x={DX} y={DY + kanali * 44 + 8} className="shema-t-muted">сваки број је од 0 до 255</text>
    </svg>
  )
}
