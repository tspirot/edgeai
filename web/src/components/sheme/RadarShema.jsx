/* Радар: од (угао, удаљеност) до тачке на екрану. Исте формуле као у lidar.py:
   x = cx + d·sin(a), y = cy − d·cos(a). Угао 0° је право напред (врх екрана). */

export default function RadarShema({ data = {}, boja = 'currentColor' }) {
  const {
    domet = 4,
    tacke = [
      { a: 20, d: 1.1 }, { a: 28, d: 1.0 }, { a: 36, d: 1.05 },
      { a: 110, d: 2.6 }, { a: 118, d: 2.5 },
      { a: 200, d: 3.4 }, { a: 215, d: 3.3 }, { a: 230, d: 3.4 },
      { a: 305, d: 1.8 }, { a: 312, d: 1.7 },
    ],
    izabrana = { a: 110, d: 2.6 },
  } = data
  const cx = 170
  const cy = 130
  const R = 110
  const px = (a, d) => cx + (d / domet) * R * Math.sin((a * Math.PI) / 180)
  const py = (a, d) => cy - (d / domet) * R * Math.cos((a * Math.PI) / 180)

  return (
    <svg
      viewBox="0 0 560 260"
      className="shema-svg"
      role="img"
      aria-label={`Радарски приказ на ${domet} метра. Свака тачка има угао и удаљеност; пример: ${izabrana.a} степени и ${izabrana.d} метра. Нула степени је право напред.`}
    >
      {[0.25, 0.5, 0.75, 1].map((k) => (
        <circle key={k} cx={cx} cy={cy} r={R * k} className="shema-zona" />
      ))}
      {[0, 90, 180, 270].map((a) => (
        <g key={a}>
          <line x1={cx} y1={cy} x2={px(a, domet)} y2={py(a, domet)} className="shema-veza" strokeWidth="1" />
          <text x={px(a, domet * 1.16) - 8} y={py(a, domet * 1.16) + 4} className="shema-t-mini">{a}°</text>
        </g>
      ))}
      <text x={cx + R * 0.5 + 4} y={cy + 14} className="shema-t-mini">{domet / 2} m</text>
      <text x={cx + R + 4} y={cy + 14} className="shema-t-mini">{domet} m</text>

      {tacke.map((t, i) => (
        <circle key={i} cx={px(t.a, t.d)} cy={py(t.a, t.d)} r="3.2" fill={boja} opacity="0.8" />
      ))}

      {/* изабрана тачка */}
      <line x1={cx} y1={cy} x2={px(izabrana.a, izabrana.d)} y2={py(izabrana.a, izabrana.d)}
        stroke={boja} strokeWidth="2" strokeDasharray="5 3" />
      <circle cx={px(izabrana.a, izabrana.d)} cy={py(izabrana.a, izabrana.d)} r="7"
        fill="none" stroke={boja} strokeWidth="2.5" />
      <circle cx={cx} cy={cy} r="6" fill="var(--ink)" />
      <text x={cx - 22} y={cy + 24} className="shema-t-mini">LiDAR</text>

      {/* формуле */}
      <text x="340" y="52" className="shema-t-ink">једно мерење =</text>
      <text x="340" y="74" className="shema-t-port">угао {izabrana.a}°, {izabrana.d} m</text>
      <text x="340" y="112" className="shema-t-ink">у пикселе:</text>
      <text x="340" y="134" className="shema-t-port">x = cx + d · sin(угао)</text>
      <text x="340" y="154" className="shema-t-port">y = cy − d · cos(угао)</text>
      <text x="340" y="192" className="shema-t-muted">0° је право напред (врх екрана),</text>
      <text x="340" y="210" className="shema-t-muted">угао расте у смеру казаљке.</text>
    </svg>
  )
}
