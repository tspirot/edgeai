/* Рендерер за садржај страна описан низом блокова (data/*.js). */

function Block({ b }) {
  switch (b.type) {
    case 'p':
      return <p className={b.lead ? 'lead' : undefined}>{b.text}</p>
    case 'h':
      return <h2>{b.text}</h2>
    case 'h3':
      return <h3>{b.text}</h3>
    case 'ul':
      return (
        <ul>
          {b.items.map((it, i) => <li key={i}>{it}</li>)}
        </ul>
      )
    case 'ol':
      return (
        <ol>
          {b.items.map((it, i) => <li key={i}>{it}</li>)}
        </ol>
      )
    case 'steps':
      return (
        <ol className="steps">
          {b.items.map((it, i) => <li key={i}>{it}</li>)}
        </ol>
      )
    case 'code':
      return (
        <pre>
          <code>{b.code}</code>
        </pre>
      )
    case 'callout':
      return (
        <aside className={`callout callout--${b.tone || 'info'}`}>
          {b.title && <strong>{b.title}</strong>}
          <p>{b.text}</p>
        </aside>
      )
    case 'specs':
      return (
        <ul className="specs">
          {b.items.map((s, i) => <li key={i}><span>{s}</span></li>)}
        </ul>
      )
    case 'quote':
      return (
        <blockquote>
          {b.text}
          {b.cite && <cite>{b.cite}</cite>}
        </blockquote>
      )
    default:
      return null
  }
}

export default function Content({ blocks }) {
  return (
    <div className="prose">
      {blocks.map((b, i) => <Block key={i} b={b} />)}
    </div>
  )
}
