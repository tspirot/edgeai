import { useState, useEffect, useRef } from 'react'

const SAMPLES = [
  'Добро дошли на Edge AI радионицу Техничке школе Пирот.',
  'Вештачка интелигенција ради локално на Raspberry Pi плочи.',
  'Звук из учионице се обрађује у меморији и нигде се не шаље.',
]

export default function CaptionSimulator() {
  const [selectedSample, setSelectedSample] = useState(0)
  const [customText, setCustomText] = useState('')
  const [isRunning, setIsRunning] = useState(false)
  const [confirmedWords, setConfirmedWords] = useState([])
  const [tentativeWords, setTentativeWords] = useState([])
  const [latency, setLatency] = useState(318)
  const timerRef = useRef(null)

  const activeText = customText.trim() || SAMPLES[selectedSample]
  const words = activeText.split(/\s+/)

  const startSimulation = () => {
    if (isRunning) return
    setIsRunning(true)
    setConfirmedWords([])
    setTentativeWords([])

    let step = 0
    const totalWords = words.length

    if (timerRef.current) clearInterval(timerRef.current)

    timerRef.current = setInterval(() => {
      step++
      // Случајна симулација латенције између 290 и 340ms
      setLatency(Math.floor(290 + Math.random() * 50))

      if (step <= totalWords) {
        // Речи до step-1 су потврђене (LocalAgreement), последња реч је хипотеза
        const confirmed = words.slice(0, Math.max(0, step - 1))
        const tentative = [words[step - 1]]
        setConfirmedWords(confirmed)
        setTentativeWords(tentative)
      } else if (step === totalWords + 1) {
        // Све речи су потврђене
        setConfirmedWords(words)
        setTentativeWords([])
        setIsRunning(false)
        clearInterval(timerRef.current)
      }
    }, 480)
  }

  const resetSimulation = () => {
    if (timerRef.current) clearInterval(timerRef.current)
    setIsRunning(false)
    setConfirmedWords([])
    setTentativeWords([])
  }

  useEffect(() => {
    return () => {
      if (timerRef.current) clearInterval(timerRef.current)
    }
  }, [])

  return (
    <div className="caption-sim">
      <div className="caption-sim__head">
        <div className="caption-sim__badge">
          <span className="caption-sim__pulse" />
          <span>Интерактивна симулација: LocalAgreement алгоритам</span>
        </div>
        <div className="caption-sim__telemetry">
          <span>Латенција: <strong>{latency} ms</strong></span>
          <span>Офлајн: <strong>100%</strong></span>
          <span>CPU оптерећење: <strong>~32%</strong></span>
        </div>
      </div>

      <div className="caption-sim__screen">
        <div className="caption-sim__monitor">
          <div className="caption-sim__monitor-top">
            <span className="caption-sim__window-dot dot-red" />
            <span className="caption-sim__window-dot dot-yellow" />
            <span className="caption-sim__window-dot dot-green" />
            <span className="caption-sim__window-title">HDMI приказ уживо (1920 × 1080)</span>
          </div>

          <div className="caption-sim__text-area">
            {confirmedWords.length === 0 && tentativeWords.length === 0 ? (
              <span className="caption-sim__placeholder">
                Кликни на „Покрени симулацију говора“ испод да видиш како речи стижу у реалном времену без треперења...
              </span>
            ) : (
              <p className="caption-sim__text">
                {confirmedWords.map((word, i) => (
                  <span key={i} className="caption-word caption-word--confirmed">
                    {word}{' '}
                  </span>
                ))}
                {tentativeWords.map((word, i) => (
                  <span key={`t-${i}`} className="caption-word caption-word--tentative">
                    {word}{' '}
                  </span>
                ))}
                {isRunning && <span className="caption-sim__cursor">▋</span>}
              </p>
            )}
          </div>

          <div className="caption-sim__legend">
            <span className="legend-item">
              <i className="legend-box legend-box--green" />
              Потврђена реч (појавила се у 2 узастопна прозора — фиксирана)
            </span>
            <span className="legend-item">
              <i className="legend-box legend-box--gray" />
              Тренутна хипотеза (чека потврду)
            </span>
          </div>
        </div>
      </div>

      <div className="caption-sim__controls">
        <div className="caption-sim__samples">
          <span className="caption-sim__label">Примери реченица:</span>
          <div className="caption-sim__buttons">
            {SAMPLES.map((sample, idx) => (
              <button
                key={idx}
                type="button"
                className={`btn btn--sm ${selectedSample === idx && !customText ? 'btn--primary' : 'btn--ghost'}`}
                onClick={() => {
                  setSelectedSample(idx)
                  setCustomText('')
                  resetSimulation()
                }}
              >
                Пример {idx + 1}
              </button>
            ))}
          </div>
        </div>

        <div className="caption-sim__custom">
          <input
            type="text"
            className="caption-sim__input"
            placeholder="Или упиши своју реченицу на српском..."
            value={customText}
            onChange={(e) => {
              setCustomText(e.target.value)
              resetSimulation()
            }}
          />
        </div>

        <div className="caption-sim__action">
          <button
            type="button"
            className="btn btn--primary"
            onClick={startSimulation}
            disabled={isRunning}
          >
            {isRunning ? 'Титловање у току...' : '▶ Покрени симулацију говора'}
          </button>
          {(confirmedWords.length > 0 || tentativeWords.length > 0) && (
            <button
              type="button"
              className="btn btn--ghost btn--sm"
              onClick={resetSimulation}
              disabled={isRunning}
            >
              Ресетуј
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

