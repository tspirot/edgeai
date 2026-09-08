---
name: deploy
description: Deploy the Edge AI site (web/) to edgeai.tsp.edu.rs. Deploy is automatic via GitHub webhook → PM2 Node service → deploy.sh on the Virtualmin server. Use when asked to deploy, publish, push the site live, or debug the deploy.
---

# Deploy сајта на edgeai.tsp.edu.rs

Механизам (исти као tsp портал, **без SSH**, auth **преко secret-а**):

```
git push main ──► https://edgeai.tsp.edu.rs/webhook  (Apache proxy)
             ──► 127.0.0.1:9008  deploy/webhook-server.js  (PM2: edgeai-webhook)
             ──► deploy/deploy.sh:  git reset --hard → npm ci → npm run build
                                    → backup public_html → rsync web/dist → public_html
                                    (build падне → rollback)
```

## Свакодневни deploy

**Ништа посебно — само `git push` у `main`.** Ако push дира `web/**` или `deploy/**`,
webhook сам преведе и објави сајт за ~1 минут.

Ручни deploy на серверу: `bash ~/edgeai/deploy/deploy.sh`

## Провера

- `curl https://edgeai.tsp.edu.rs/webhook/health` → `ok` (webhook жив)
- `https://edgeai.tsp.edu.rs/` се учита, 3D сцена ради
- директан улаз на `/projekti/titlovi-uzivo` не даје 404 (`.htaccess` ради)
- логови: `deploy/logs/webhook.log`, `deploy/logs/deploy.log`

## Ако deploy не ради

1. GitHub → repo Settings → Webhooks → Recent Deliveries — види одговор (треба 202).
   `401` = погрешан secret (упореди са `WEBHOOK_SECRET` у `deploy/ecosystem.config.js`).
   Timeout/`502` = Node сервис или Apache proxy пали.
2. На серверу: `pm2 status`, `pm2 logs edgeai-webhook`.
3. `deploy/logs/deploy.log` — ако је build пао, `rollback` враћа претходну верзију,
   па сајт ради, али је стар. Поправи узрок и `git push` поново.

## Прва поставка на новом серверу

Види `deploy/README.md` (клон са PAT-ом, `pm2 start deploy/ecosystem.config.js`,
Apache `ProxyPass /webhook`, GitHub webhook).
