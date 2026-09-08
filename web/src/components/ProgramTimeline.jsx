export default function ProgramTimeline({ aktivnosti }) {
  // Додатни метаподаци за инжењерски тајмлајн ако нису у самом JSON-у
  const meta = [
    { period: 'Фаза 1 · Поставка', status: 'завршено', ishod: 'Постављених 5 лабораторијских станица + Makers Lab 3D штампа' },
    { period: 'Фаза 2 · Припрема', status: 'у току', ishod: 'Техничка упутства, скуп података и превођење модела у int8' },
    { period: 'Фаза 3 · Развој', status: 'у току', ishod: '5 тимова ученика програмира и тестира хардверске прототипове' },
    { period: 'Фаза 4 · Завршница', status: 'планирано', ishod: 'Јавна презентација у ZIP Центру Пирот, мерења латенције уживо' },
  ]

  return (
    <div className="timeline">
      {aktivnosti.map((a, idx) => {
        const m = meta[idx] || {}
        const isDone = m.status === 'завршено'
        const isInProgress = m.status === 'у току'

        return (
          <div key={a.broj} className={`timeline-item ${isDone ? 'is-done' : ''} ${isInProgress ? 'is-current' : ''}`}>
            <div className="timeline-item__axis">
              <div className="timeline-item__node">
                <span>0{a.broj}</span>
              </div>
              {idx < aktivnosti.length - 1 && <div className="timeline-item__line" />}
            </div>

            <div className="timeline-item__body">
              <div className="timeline-item__meta">
                <span className="timeline-item__period">{m.period}</span>
                <span
                  className={`tag ${isDone ? 'tag--status' : isInProgress ? 'tag--hw' : ''}`}
                >
                  {m.status}
                </span>
              </div>

              <h3 className="timeline-item__title">{a.naziv}</h3>
              <p className="timeline-item__text">{a.tekst}</p>

              {m.ishod && (
                <div className="timeline-item__outcome">
                  <strong>Кључни резултат:</strong> {m.ishod}
                </div>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

