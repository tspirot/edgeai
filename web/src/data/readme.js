/* README-и пројеката (projekti/<slug>/README.md), увезени у build преко ?raw.
   Приказују се на дну упутства везаног за пројекат (види pages/Uputstvo.jsx). */

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
