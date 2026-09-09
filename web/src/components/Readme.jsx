import { useMemo } from 'react'
import { Marked } from 'marked'

/* README пројекта (markdown из репоа) → HTML.
   Наслови се спуштају за један ниво да h1 из README-ја не удара у h1 стране. */
const renderer = {
  heading({ tokens, depth }) {
    const d = Math.min(depth + 1, 6)
    return `<h${d}>${this.parser.parseInline(tokens)}</h${d}>\n`
  },
}

const md = new Marked({ gfm: true, breaks: false })
md.use({ renderer })

export default function Readme({ markdown }) {
  const html = useMemo(() => md.parse(markdown), [markdown])
  return (
    <div
      className="prose readme"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
