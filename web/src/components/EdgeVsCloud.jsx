import { useState } from 'react'

export default function EdgeVsCloud() {
  const [mode, setMode] = useState('edge') // 'edge' | 'cloud'

  const isEdge = mode === 'edge'

  return (
    <div className="compare-box">
      <div className="compare-box__header">
        <div className="compare-toggle">
          <button
            type="button"
            className={`compare-toggle__btn ${isEdge ? 'is-active is-edge' : ''}`}
            onClick={() => setMode('edge')}
          >
            <span className="compare-toggle__dot" />
            Локално на плочи (Edge AI)
          </button>
          <button
            type="button"
            className={`compare-toggle__btn ${!isEdge ? 'is-active is-cloud' : ''}`}
            onClick={() => setMode('cloud')}
          >
            <span className="compare-toggle__dot" />
            У облаку (Cloud AI)
          </button>
        </div>

        <div className={`compare-status ${isEdge ? 'compare-status--edge' : 'compare-status--cloud'}`}>
          {isEdge ? (
            <>
              <span className="compare-status__icon">🛡️</span>
              <span><strong>Офлајн режим:</strong> Звук и слика не напуштају уређај</span>
            </>
          ) : (
            <>
              <span className="compare-status__icon">📡</span>
              <span><strong>Зависност од мреже:</strong> Подаци путују на удаљени сервер</span>
            </>
          )}
        </div>
      </div>

      <div className="compare-grid">
        {/* Метрика 1: Латенција */}
        <div className="compare-metric">
          <div className="compare-metric__top">
            <span className="compare-metric__label">Брзина одзива (латенција)</span>
            <span className={`compare-metric__val ${isEdge ? 'text-accent' : 'text-alert'}`}>
              {isEdge ? '~15 – 80 ms' : '~450 – 1500 ms'}
            </span>
          </div>
          <div className="compare-bar">
            <div
              className={`compare-bar__fill ${isEdge ? 'compare-bar__fill--fast' : 'compare-bar__fill--slow'}`}
              style={{ width: isEdge ? '14%' : '88%' }}
            />
          </div>
          <p className="compare-metric__desc">
            {isEdge
              ? 'Резултат стиже моментално директно из NPU/CPU чипа.'
              : 'Кашњење због слања звука/слике преко интернета и чекања у реду.'}
          </p>
        </div>

        {/* Метрика 2: Интернет саобраћај */}
        <div className="compare-metric">
          <div className="compare-metric__top">
            <span className="compare-metric__label">Интернет проток</span>
            <span className={`compare-metric__val ${isEdge ? 'text-accent' : 'text-brass'}`}>
              {isEdge ? '0 KB/s (нема везе)' : '2 – 10 MB / мин'}
            </span>
          </div>
          <div className="compare-bar">
            <div
              className={`compare-bar__fill ${isEdge ? 'compare-bar__fill--zero' : 'compare-bar__fill--data'}`}
              style={{ width: isEdge ? '2%' : '75%' }}
            />
          </div>
          <p className="compare-metric__desc">
            {isEdge
              ? 'Ради пуним капацитетом на планини, у сали, у подруму.'
              : 'Ако падне Wi-Fi или школа нема сигнал — систем стаје.'}
          </p>
        </div>

        {/* Метрика 3: Приватност */}
        <div className="compare-metric">
          <div className="compare-metric__top">
            <span className="compare-metric__label">Приватност и подаци</span>
            <span className={`compare-metric__val ${isEdge ? 'text-accent' : 'text-alert'}`}>
              {isEdge ? '100% заштићено' : 'Слање трећем лицу'}
            </span>
          </div>
          <div className="compare-bar">
            <div
              className={`compare-bar__fill ${isEdge ? 'compare-bar__fill--safe' : 'compare-bar__fill--risk'}`}
              style={{ width: '100%' }}
            />
          </div>
          <p className="compare-metric__desc">
            {isEdge
              ? 'Микрофон и камера се обрађују у RAM-у и одмах бришу.'
              : 'Аудио и видео снимци се шаљу на комерцијалне сервере у иностранству.'}
          </p>
        </div>

        {/* Метрика 4: Трошкови */}
        <div className="compare-metric">
          <div className="compare-metric__top">
            <span className="compare-metric__label">Трошкови рада</span>
            <span className={`compare-metric__val ${isEdge ? 'text-accent' : 'text-brass'}`}>
              {isEdge ? '0 RSD / упит' : 'Претплата + по упиту'}
            </span>
          </div>
          <div className="compare-bar">
            <div
              className={`compare-bar__fill ${isEdge ? 'compare-bar__fill--free' : 'compare-bar__fill--cost'}`}
              style={{ width: isEdge ? '5%' : '65%' }}
            />
          </div>
          <p className="compare-metric__desc">
            {isEdge
              ? 'Само утрошена струја плоче (~5 вати). Нема лиценци.'
              : 'Сваки сат рада наплаћује се по ценовнику API сервиса.'}
          </p>
        </div>
      </div>
    </div>
  )
}

