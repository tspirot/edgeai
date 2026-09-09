/* Рендерер за садржај страна описан низом блокова (data/*.js). */

import Figure from './Figure'
import Galerija from './Galerija'
import Shema from './Shema'

function Block({ b, boja }) {
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
    case 'figure':
      return <Figure {...b} />
    case 'galerija':
      return <Galerija items={b.items} caption={b.caption} />
    case 'shema':
      // `boja` пада са стране пројекта ако блок не наведе своју.
      return <Shema {...b} boja={b.boja || boja} />
    default:
      return null
  }
}

export default function Content({ blocks, boja }) {
  return (
    <div className="prose">
      {blocks.map((b, i) => <Block key={i} b={b} boja={boja} />)}
    </div>
  )
}
