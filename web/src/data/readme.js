/* README-и пројеката (projekti/<slug>/README.md) и примера (lms/primeri/<folder>/README.md),
   увезени у build преко ?raw. Пројектни се приказују на дну упутства везаног за пројекат
   (pages/Uputstvo.jsx), примера на страни примера (pages/Primer.jsx). */

const files = import.meta.glob('../../../projekti/*/README.md', {
  query: '?raw',
  import: 'default',
  eager: true,
})

/* GitHub README-и имају на врху значке и табелу „Преглед“ (између маркера <!-- …:почетак --> и
   <!-- …:крај -->), а на дну одељак о приватности са релативним везама. На сајту то дуплира
   страницу пројекта, па се ти блокови овде уклањају. */
const GENERISANO = /<!-- (значке|преглед|приватност):почетак -->[\s\S]*?<!-- \1:крај -->\n*/g

const readmeBySlug = {}
for (const [put, sadrzaj] of Object.entries(files)) {
  const m = put.match(/projekti\/([^/]+)\/README\.md$/)
  if (m) readmeBySlug[m[1]] = sadrzaj.replace(/\r\n/g, '\n').replace(GENERISANO, '')
}

export const getReadme = (slug) => readmeBySlug[slug] || null

const primeriFiles = import.meta.glob('../../../lms/primeri/**/README.md', {
  query: '?raw',
  import: 'default',
  eager: true,
})

/* README-и ових фолдера су за GitHub (значке, релативне везе), а страница примера на
   сајту већ показује исто: покретање, тастере и лекцију. Зато се овде не увлаче. */
const BEZ_README_NA_SAJTU = new Set([
  'uvod', 'test',
])

const readmeByFolder = {}
for (const [put, sadrzaj] of Object.entries(primeriFiles)) {
  const m = put.match(/lms\/primeri\/(.+)\/README\.md$/)
  if (m && !BEZ_README_NA_SAJTU.has(m[1])) {
    readmeByFolder[m[1]] = sadrzaj
    // Такође региструј под последњим делом путање (нпр. 'crtanje' за 'igrice/crtanje')
    const delovi = m[1].split('/')
    const base = delovi[delovi.length - 1]
    if (base && !readmeByFolder[base]) {
      readmeByFolder[base] = sadrzaj
    }
  }
}

export const getPrimerReadme = (folder) => readmeByFolder[folder] || null
