/* Око као шест тачака: основа за EAR (Eye Aspect Ratio) у примеру „Вози безбедно“.
   Две усправне удаљености и једна водоравна; кад се око склопи, прве се скупе
   а трећа остаје — зато количник пада. */

// Распоред као у коду: p1 лево, p2/p3 горе, p4 десно, p5/p6 доле.
const TACKE = {
  p1: [60, 100],
  p2: [120, 58],
  p3: [200, 58],
  p4: [260, 100],
  p5: [200, 142],
  p6: [120, 142],
}

export default function OkoShema({ data = {}, boja = 'currentColor' }) {
  const { otvoreno = 0.30, zatvoreno = 0.08, prag = 0.22 } = data
  const sirina = 320
  const spoljna =
    `M${TACKE.p1} Q${TACKE.p2[0] - 10},${TACKE.p2[1] - 22} ${TACKE.p2} ` +
    `L${TACKE.p3} Q${TACKE.p3[0] + 10},${TACKE.p3[1] - 22} ${TACKE.p4} ` +
    `Q${TACKE.p5[0] + 10},${TACKE.p5[1] + 22} ${TACKE.p5} L${TACKE.p6} ` +
    `Q${TACKE.p6[0] - 10},${TACKE.p6[1] + 22} ${TACKE.p1} Z`

  const traka = (y, v, naziv, ok) => (
    <g>
      <text x={sirina + 40} y={y - 6} className="shema-t-ink">{naziv}</text>
      <rect x={sirina + 40} y={y} width={150} height={16} rx="4" className="shema-box" />
      <rect x={sirina + 40} y={y} width={Math.min(150, (150 * v) / 0.45)} height={16} rx="4"
        fill={ok ? boja : 'var(--alert)'} opacity="0.8" />
      <text x={sirina + 198} y={y + 13} className="shema-t-ink">{v.toFixed(2)}</text>
    </g>
  )

  return (
    <svg
      viewBox="0 0 580 210"
      className="shema-svg"
      role="img"
      aria-label={`Око означено са шест тачака. EAR је збир две усправне удаљености подељен двоструком водоравном. Отворено око даје око ${otvoreno}, склопљено око око ${zatvoreno}, а праг је ${prag}.`}
    >
      <path d={spoljna} className="shema-box" />
      <circle cx="160" cy="100" r="22" fill={boja} opacity="0.25" />
      <circle cx="160" cy="100" r="9" fill={boja} opacity="0.7" />

      {/* удаљености */}
      <line x1={TACKE.p2[0]} y1={TACKE.p2[1]} x2={TACKE.p6[0]} y2={TACKE.p6[1]} stroke={boja} strokeWidth="2" strokeDasharray="4 3" />
      <line x1={TACKE.p3[0]} y1={TACKE.p3[1]} x2={TACKE.p5[0]} y2={TACKE.p5[1]} stroke={boja} strokeWidth="2" strokeDasharray="4 3" />
      <line x1={TACKE.p1[0]} y1="176" x2={TACKE.p4[0]} y2="176" className="shema-veza" />
      <text x="160" y="196" className="shema-t-muted" textAnchor="middle">водоравно: p1 – p4</text>

      {Object.entries(TACKE).map(([k, [x, y]]) => (
        <g key={k}>
          <circle cx={x} cy={y} r="5" fill={boja} />
          <text
            x={x + (k === 'p1' ? -18 : k === 'p4' ? 12 : -4)}
            y={y + (k === 'p5' || k === 'p6' ? 22 : k === 'p2' || k === 'p3' ? -12 : 4)}
            className="shema-t-port"
          >
            {k}
          </text>
        </g>
      ))}

      <text x="160" y="22" className="shema-t-ink" textAnchor="middle">EAR = (|p2–p6| + |p3–p5|) / (2 · |p1–p4|)</text>

      {/* вредности */}
      {traka(52, otvoreno, 'отворено око', true)}
      {traka(100, zatvoreno, 'склопљено око', false)}
      <line
        x1={sirina + 40 + (150 * prag) / 0.45} y1="40"
        x2={sirina + 40 + (150 * prag) / 0.45} y2="122"
        stroke="var(--alert)" strokeWidth="1.5" strokeDasharray="3 3"
      />
      <text x={sirina + 40 + (150 * prag) / 0.45} y="140" className="shema-t-mini" textAnchor="middle">праг {prag}</text>
    </svg>
  )
}
