// PM2 конфигурација за webhook сервис (исти приступ као tsp портал).
// Сервер: Virtualmin, корисник `edgeai`, home `/home/edgeai`, docroot `~/public_html`.
// Покретање:  pm2 start deploy/ecosystem.config.js
//
// ТАЈНА СЕ НЕ УПИСУЈЕ У ОВАЈ ФАЈЛ (он је у git-у). WEBHOOK_SECRET се чита из
// променљиве окружења или из `deploy/.env` на серверу (игнорисан у git-у,
// deploy.sh га не брише). Мора бити идентичан као у GitHub → Settings → Webhooks.
// Види deploy/.env.example.

const fs = require('fs')
const path = require('path')

function procitajEnv(putanja) {
  const out = {}
  let tekst
  try { tekst = fs.readFileSync(putanja, 'utf8') } catch { return out }
  for (const red of tekst.split(/\r?\n/)) {
    const m = red.match(/^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$/)
    if (m && !red.trim().startsWith('#')) out[m[1]] = m[2].replace(/^(['"])(.*)\1$/, '$2')
  }
  return out
}

const tajna = process.env.WEBHOOK_SECRET || procitajEnv(path.join(__dirname, '.env')).WEBHOOK_SECRET
if (!tajna) {
  throw new Error(
    'WEBHOOK_SECRET није подешен. Направи deploy/.env (види deploy/.env.example) ' +
    'или извези WEBHOOK_SECRET пре `pm2 start`.',
  )
}

module.exports = {
  apps: [
    {
      name: 'edgeai-webhook',
      cwd: '/home/edgeai/edgeai',
      script: 'deploy/webhook-server.js',
      time: true,
      env: {
        NODE_ENV: 'production',
        WEBHOOK_PORT: 9008,
        WEBHOOK_SECRET: tajna,
        DEPLOY_BRANCH: 'main',
        REPO_DIR: '/home/edgeai/edgeai',
        PUBLIC_HTML: '/home/edgeai/public_html',
      },
    },
  ],
}
