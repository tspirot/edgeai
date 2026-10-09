/* Везе ка репоу на GitHub-у: једно место за адресу и грану.
   Репо је приватан — везе отвара само ко има приступ (иначе GitHub даје 404). */

export const GH_REPO = 'https://github.com/tspirot/edgeai'
export const GH_BRANCH = 'main'

/** Фолдер: ghTree('lms/primeri/test'). */
export const ghTree = (putanja = '') =>
  putanja ? `${GH_REPO}/tree/${GH_BRANCH}/${putanja}` : GH_REPO

/** Датотека: ghBlob('LICENSE'). */
export const ghBlob = (putanja) => `${GH_REPO}/blob/${GH_BRANCH}/${putanja}`

/** Уређивање датотеке у прегледачу: ghEdit('web/src/data/lms.js'). */
export const ghEdit = (putanja) => `${GH_REPO}/edit/${GH_BRANCH}/${putanja}`
