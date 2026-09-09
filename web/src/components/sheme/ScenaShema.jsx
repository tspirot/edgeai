import { useIsNarrow } from '../../lib/hooks'

/* Поглед одозго на сцену: где стоји камера, докле јој сеже видно поље,
   које су зоне детекције и шта се у њима појављује.
   Координате објеката су у процентима, па распоред ради на свакој ширини. */

export default function ScenaShema({ data, boja = 'currentColor' }) {
  const usko = useIsNarrow()
  if (!data?.kamera) return null

  const { kamera, zone = [], objekti = [], tlo } = data
  const W = usko ? 340 : 680
  const H = usko ? 400 : 380
  const apexY = 40
  const vfov = kamera.vfov || 62
  const domet = H - apexY - 14
  const polusirina = Math.min(W / 2 - 6, Math.tan((vfov / 2) * (Math.PI / 180)) * domet)
  const cx = W / 2

  const opis = `Поглед одозго: ${kamera.naziv}, видно поље ${vfov}°${
    zone.length ? `, зоне: ${zone.map((z) => z.naziv).join(', ')}` : ''
  }.`

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="shema-svg" role="img" aria-label={opis}>
      {/* тло */}
      <rect x="0" y={apexY} width={W} height={H - apexY} rx="12" className="shema-tlo" />

      {/* конус видног поља */}
      <polygon
        points={`${cx},${apexY} ${cx - polusirina},${apexY + domet} ${cx + polusirina},${apexY + domet}`}
        fill={boja} opacity="0.10"
      />
      <polygon
        points={`${cx},${apexY} ${cx - polusirina},${apexY + domet} ${cx + polusirina},${apexY + domet}`}
        fill="none" stroke={boja} strokeWidth="1.2" strokeDasharray="5 5" opacity="0.55"
      />

      {/* зоне детекције */}
      {zone.map((z, i) => {
        const y1 = apexY + (domet * z.od) / 100
        const y2 = apexY + (domet * z.do) / 100
        return (
          <g key={i}>
            <rect x="10" y={y1} width={W - 20} height={y2 - y1} rx="8"
              className="shema-zona" />
            <text x="20" y={y1 + 17} className="shema-t-port">{z.naziv}</text>
          </g>
        )
      })}

      {/* објекти у сцени */}
      {objekti.map((o, i) => {
        const x = (W * o.x) / 100
        const y = apexY + (domet * o.y) / 100
        return (
          <g key={i}>
            <circle cx={x} cy={y} r="15" className="shema-objekat" />
            <text x={x} y={y + 6} className="shema-emoji" textAnchor="middle">{o.ikona}</text>
            <text x={x} y={y + 32} className="shema-t-mini" textAnchor="middle">{o.naziv}</text>
          </g>
        )
      })}

      {/* камера — сви подаци у једном реду изнад врха конуса, без преклапања */}
      <circle cx={cx} cy={apexY} r="13" fill={boja} opacity="0.9" />
      <text x={cx} y={apexY + 5} className="shema-emoji" textAnchor="middle">📷</text>
      <text x={cx} y="12" className="shema-t-ink" textAnchor="middle">{kamera.naziv}</text>
      <text x={cx} y="25" className="shema-t-port" textAnchor="middle">
        {[`${vfov}°`, kamera.visina].filter(Boolean).join(' · ')}
      </text>

      {tlo && <text x={W / 2} y={H - 4} className="shema-t-mini" textAnchor="middle">{tlo}</text>}
    </svg>
  )
}
