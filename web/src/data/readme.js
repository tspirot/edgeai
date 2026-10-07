/* README-и пројеката (projekti/<slug>/README.md) и примера (lms/primeri/<folder>/README.md),
   увезени у build преко ?raw. Пројектни се приказују на дну упутства везаног за пројекат
   (pages/Uputstvo.jsx), примера на страни примера (pages/Primer.jsx). */

const files = import.meta.glob('../../../projekti/*/README.md', {
  query: '?raw',
  import: 'default',
  eager: true,
})

const readmeBySlug = {}
for (const [put, sadrzaj] of Object.entries(files)) {
  const m = put.match(/projekti\/([^/]+)\/README\.md$/)
  if (m) readmeBySlug[m[1]] = sadrzaj
}

export const getReadme = (slug) => readmeBySlug[slug] || null

const primeriFiles = import.meta.glob('../../../lms/primeri/*/README.md', {
  query: '?raw',
  import: 'default',
  eager: true,
})

const readmeByFolder = {}
for (const [put, sadrzaj] of Object.entries(primeriFiles)) {
  const m = put.match(/lms\/primeri\/([^/]+)\/README\.md$/)
  if (m) readmeByFolder[m[1]] = sadrzaj
}

export const getPrimerReadme = (folder) => readmeByFolder[folder] || null
