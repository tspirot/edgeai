export default function ProjectTelemetry({ telemetrija }) {
  if (!telemetrija) return null

  const items = [
    { label: 'Латенција инференце', value: telemetrija.latencija, icon: '⏱️', hot: true },
    { label: 'Процесор / NPU', value: telemetrija.npuCpu, icon: '⚡' },
    { label: 'Радна потрошња', value: telemetrija.potrosnja, icon: '🔋' },
    { label: 'Режим рада', value: telemetrija.offline, icon: '🛡️', ok: true },
    telemetrija.fps ? { label: 'Брзина кадрова', value: telemetrija.fps, icon: '🎞️' } : null,
    telemetrija.memorija ? { label: 'RAM меморија', value: telemetrija.memorija, icon: '💾' } : null,
    telemetrija.baterija ? { label: 'Аутономија рада', value: telemetrija.baterija, icon: '🔋' } : null,
    { label: 'AI Модел', value: telemetrija.model, icon: '🧠' },
  ].filter(Boolean)

  return (
    <div className="telemetry-bar">
      <div className="telemetry-bar__label">
        <span className="telemetry-bar__dot" />
        <span>Лабораторијска телеметрија прототипа</span>
      </div>
      <div className="telemetry-grid">
        {items.map((item, idx) => (
          <div key={idx} className="telemetry-item">
            <div className="telemetry-item__top">
              <span className="telemetry-item__icon">{item.icon}</span>
              <span className="telemetry-item__label">{item.label}</span>
            </div>
            <div className={`telemetry-item__val ${item.hot ? 'is-hot' : ''} ${item.ok ? 'is-ok' : ''}`}>
              {item.value}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

