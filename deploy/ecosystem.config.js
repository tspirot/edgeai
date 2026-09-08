// PM2 конфигурација за webhook сервис (исти приступ као tsp портал).
// Сервер: Virtualmin, корисник `edgeai`, home `/home/edgeai`, docroot `~/public_html`.
// Покретање:  pm2 start deploy/ecosystem.config.js
//
// WEBHOOK_SECRET мора бити идентичан као у GitHub → Settings → Webhooks.

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
        WEBHOOK_SECRET: '75ebfa5729869d31e02f168956db798205a99bd50e1030345629343c3bced226',
        DEPLOY_BRANCH: 'main',
        REPO_DIR: '/home/edgeai/edgeai',
        PUBLIC_HTML: '/home/edgeai/public_html',
      },
    },
  ],
}
