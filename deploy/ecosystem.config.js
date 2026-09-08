// PM2 конфигурација за webhook сервис (исти приступ као tsp портал).
// Постави праве путање (USER) и покрени:  pm2 start deploy/ecosystem.config.js
//
// WEBHOOK_SECRET мора бити идентичан као у GitHub → Settings → Webhooks.
// Репо је приватан/интерни, па секрет овде смета мање него код јавних репоа;
// ако желиш да га извучеш, стави га у ~/.edgeai.env и учитај преко env_file.

module.exports = {
  apps: [
    {
      name: 'edgeai-webhook',
      cwd: '/home/USER/edgeai',
      script: 'deploy/webhook-server.js',
      time: true,
      env: {
        NODE_ENV: 'production',
        WEBHOOK_PORT: 9008,
        WEBHOOK_SECRET: '75ebfa5729869d31e02f168956db798205a99bd50e1030345629343c3bced226',
        DEPLOY_BRANCH: 'main',
        REPO_DIR: '/home/USER/edgeai',
        PUBLIC_HTML: '/home/USER/domains/edgeai.tsp.edu.rs/public_html',
      },
    },
  ],
}
