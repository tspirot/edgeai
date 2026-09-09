/* Страница кућишта за CO2 ласер: „прст“ спојеви по ивицама и отвори за портове.
   Цртеж је илустрација принципа, не радионички предложак — мере зависе
   од дебљине плексигласа и конкретне плоче. */

export default function KucisteShema({ data, boja = 'currentColor' }) {
  const W = 460
  const H = 300
  const x0 = 46
  const y0 = 40
  const pw = W - 2 * x0
  const ph = H - y0 - 52
  const zub = 16 // ширина зупца
  const dub = 9 // дубина зупца

  const otvori = data?.otvori || [
    { naziv: 'USB', x: 12, y: 62, w: 22, h: 11 },
    { naziv: 'HDMI', x: 42, y: 62, w: 26, h: 10 },
    { naziv: 'камера', x: 76, y: 20, w: 16, h: 16 },
  ]
  const vent = data?.ventilacija ?? true

  // Зупци се цртају као засебни квадратићи по ивицама — принцип, без сложене путање.
  const vodoravni = []
  for (let x = x0 + zub; x < x0 + pw - zub; x += zub * 2) {
    vodoravni.push(x)
  }
  const uspravni = []
  for (let y = y0 + zub; y < y0 + ph - zub; y += zub * 2) {
    uspravni.push(y)
  }

  return (
    <svg
      viewBox={`0 0 ${W} ${H}`}
      className="shema-svg"
      role="img"
      aria-label="Страница кућишта са „прст“ спојевима по ивицама и отворима за USB, HDMI, камеру и вентилацију."
    >
      {/* плоча */}
      <rect x={x0} y={y0} width={pw} height={ph} rx="4" className="shema-ploca" />

      {/* зупци: горе, доле, лево, десно */}
      {vodoravni.map((x) => (
        <g key={`h${x}`}>
          <rect x={x} y={y0 - dub} width={zub} height={dub} className="shema-zub" />
          <rect x={x} y={y0 + ph} width={zub} height={dub} className="shema-zub" />
        </g>
      ))}
      {uspravni.map((y) => (
        <g key={`v${y}`}>
          <rect x={x0 - dub} y={y} width={dub} height={zub} className="shema-zub" />
          <rect x={x0 + pw} y={y} width={dub} height={zub} className="shema-zub" />
        </g>
      ))}

      {/* отвори за портове */}
      {otvori.map((o, i) => {
        const ox = x0 + (pw * o.x) / 100
        const oy = y0 + (ph * o.y) / 100
        const ow = (pw * o.w) / 100
        const oh = (ph * o.h) / 100
        return (
          <g key={i}>
            <rect x={ox} y={oy} width={ow} height={oh} rx="3"
              fill={boja} opacity="0.16" stroke={boja} strokeWidth="1.3" />
            <text x={ox + ow / 2} y={oy - 6} className="shema-t-port" textAnchor="middle">{o.naziv}</text>
          </g>
        )
      })}

      {/* решетка за вентилацију */}
      {vent && (
        <g>
          {[0, 1, 2, 3, 4].map((i) => (
            <circle key={i} cx={x0 + pw * 0.24 + i * 13} cy={y0 + ph * 0.3} r="4"
              fill="none" stroke={boja} strokeWidth="1.2" opacity="0.7" />
          ))}
          <text x={x0 + pw * 0.24 + 26} y={y0 + ph * 0.3 - 14} className="shema-t-port" textAnchor="middle">
            вентилација
          </text>
        </g>
      )}

      {/* котирање */}
      <path d={`M${x0} ${y0 + ph + 26} H${x0 + pw}`} className="shema-veza" />
      <text x={x0 + pw / 2} y={y0 + ph + 42} className="shema-t-mini" textAnchor="middle">
        {data?.sirina || 'ширина по плочи — цртај у mm, размера 1:1'}
      </text>
      <text x={x0} y={y0 - 20} className="shema-t-ink">Страница кућишта</text>
      <text x={x0 + pw} y={y0 - 20} className="shema-t-port" textAnchor="end">
        дубина зупца = дебљина плексигласа
      </text>
    </svg>
  )
}
