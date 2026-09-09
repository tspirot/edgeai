import TokShema from './sheme/TokShema'

/* Ток обраде сигнала. Од верзије са графиком цртеж носи TokShema (SVG),
   а овде остају само заглавље и оквир секције. */

export default function DataPipeline({ pipeline, boja }) {
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

      <div className="pipeline-crtez">
        <TokShema pipeline={pipeline} boja={boja} />
      </div>
    </div>
  )
}
