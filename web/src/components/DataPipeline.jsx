export default function DataPipeline({ pipeline }) {
  if (!pipeline || pipeline.length === 0) return null

  return (
    <div className="pipeline-section">
      <div className="pipeline-header">
        <span className="kicker">Архитектура тока података</span>
        <h3>Ток обраде сигнала на уређају (Pipeline)</h3>
        <p>
          Сваки корак се извршава локално, без одласка на спољне сервере.
        </p>
      </div>

      <div className="pipeline-flow">
        {pipeline.map((step, idx) => (
          <div key={idx} className="pipeline-step">
            <div className="pipeline-step__num">0{idx + 1}</div>
            <div className="pipeline-step__card">
              <div className="pipeline-step__icon">{step.icon}</div>
              <div className="pipeline-step__content">
                <span className="pipeline-step__title">{step.title}</span>
                <span className="pipeline-step__detail">{step.detail}</span>
              </div>
            </div>
            {idx < pipeline.length - 1 && (
              <div className="pipeline-arrow" aria-hidden="true">
                <span>→</span>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

