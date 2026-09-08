# Deploy на edgeai.tsp.edu.rs

Два начина, оба без SSH и без GitHub Actions:

- **A) Git poll (препоручено, ништа не зависи од Apache-ја)** — cron сваких пар
  минута провери `main` и, ако има новог, покрене `deploy.sh`. Види доле.
- **B) GitHub webhook → Node сервис (PM2) → `deploy.sh`** — брже (одмах), али
  тражи да Apache/Virtualmin проксира `/webhook` на локални порт. Ако
  `curl https://edgeai.tsp.edu.rs/webhook/health` не врати `ok` него HTML,
  proxy није активан — користи начин A.

---

## A) Git poll (без Apache proxy-ја)

```bash
# репо већ клониран у ~/edgeai (види „Поставка", корак 1)
mkdir -p ~/edgeai/deploy/logs
( crontab -l 2>/dev/null | grep -v 'deploy/poll.sh'; \
  echo "*/2 * * * * /bin/bash $HOME/edgeai/deploy/poll.sh >> $HOME/edgeai/deploy/logs/poll.log 2>&1" ) | crontab -
crontab -l | grep poll     # провера
```

Од тада `git push` у `main` → сајт се сам објави за највише ~2 минута.
Лог: `~/edgeai/deploy/logs/poll.log` и `deploy.log`.
Ручно одмах: `bash ~/edgeai/deploy/deploy.sh`.

---

## B) GitHub webhook (тренутно)

Аутентикација је **преко secret-а** (HMAC `x-hub-signature-256`).

```
GitHub push ──► https://edgeai.tsp.edu.rs/webhook
                       │ Apache reverse proxy (Virtualmin)
                       ▼
             127.0.0.1:9008  webhook-server.js  (PM2: edgeai-webhook)
                       │ провери потпис, гранa = main, дира ли web/
                       ▼
                   deploy.sh
        git reset --hard → npm ci → npm run build
        backup public_html → rsync web/dist → public_html
        (ако build падне → rollback)
```

## Поставка на серверу (једном)

### 1. Клонирај репо

Приватан репо, без SSH → HTTPS remote са **fine-grained PAT** (само read за `tspirot/edgeai`):

```bash
cd ~
git clone https://x-access-token:<PAT>@github.com/tspirot/edgeai.git
```

PAT: github.com → Settings → Developer settings → Fine-grained tokens →
Repository access: само `tspirot/edgeai`, Permissions → Contents: Read-only.

### 2. Подеси PM2 сервис (без sudo)

`ecosystem.config.js` је већ намештен за корисника `edgeai` (`/home/edgeai/edgeai`,
docroot `/home/edgeai/public_html`). Провери само `WEBHOOK_SECRET`.

```bash
cd ~/edgeai
command -v pm2 || npm install pm2          # локално ако није системски (нема sudo)
PM2=$(command -v pm2 || echo ./node_modules/.bin/pm2)
$PM2 start deploy/ecosystem.config.js
$PM2 save
# аутостарт после рестарта сервера — user crontab (pm2 startup тражи root):
( crontab -l 2>/dev/null | grep -v 'pm2 resurrect'; echo "@reboot $PM2 resurrect" ) | crontab -
```

Провера: `curl http://127.0.0.1:9008/webhook/health` → `ok`.

### 3. Apache proxy (Virtualmin)

Virtualmin → домен `edgeai.tsp.edu.rs` → **Services → Configure Website → Edit Directives**,
додај у `<VirtualHost>` (и у SSL host):

```apache
ProxyPass        /webhook  http://127.0.0.1:9008/webhook
ProxyPassReverse /webhook  http://127.0.0.1:9008/webhook
```

Модули `proxy` и `proxy_http` морају бити укључени (обично јесу).
Рестарт Apache-ја. Провера: `curl https://edgeai.tsp.edu.rs/webhook/health` → `ok`.

> Остатак домена (`/`) и даље служи Apache директно из `public_html` — статички фајлови.

### 4. GitHub webhook

Repo **Settings → Webhooks → Add webhook**:

| поље | вредност |
|---|---|
| Payload URL | `https://edgeai.tsp.edu.rs/webhook` |
| Content type | `application/json` |
| Secret | иста вредност као `WEBHOOK_SECRET` у `ecosystem.config.js` |
| Events | Just the `push` event |

### 5. Прва објава

```bash
cd ~/edgeai && bash deploy/deploy.sh
```

Затим на GitHub-у: Webhooks → Recent Deliveries → **Redeliver** ping.

## Свакодневно

Само `git push` у `main`. Ако push дира `web/**` → сајт се сам преведе и објави
за ~1 минут. Логови: `deploy/logs/webhook.log` и `deploy/logs/deploy.log`.

Ручни deploy у нужди: `bash ~/edgeai/deploy/deploy.sh`.

## Потребно на серверу

`node` (18+), `npm`, `git`, `bash`, `rsync`, `pm2`. Node се у Virtualmin-у
добија преко EasyApache/„Node.js“ или `nvm`.
