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

Приватан репо, без SSH пријаве на сервер. Најбоље је **deploy key** само за читање:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/edgeai_deploy -N ""      # на серверу
cat ~/.ssh/edgeai_deploy.pub                            # додај у GitHub → репо → Settings → Deploy keys (без write)
GIT_SSH_COMMAND='ssh -i ~/.ssh/edgeai_deploy' git clone git@github.com:tspirot/edgeai.git ~/edgeai
git -C ~/edgeai config core.sshCommand 'ssh -i ~/.ssh/edgeai_deploy'
```

Ако је SSH из сервера ка GitHub-у блокиран, може fine-grained PAT (само `tspirot/edgeai`,
Contents: Read-only) у HTTPS remote-у. Тада се токен чува у `~/edgeai/.git/config`: не стављај га
у команде које се чувају у историји љуске и ротирај га редовно.

### 2. Подеси PM2 сервис (без sudo)

`ecosystem.config.js` је већ намештен за корисника `edgeai` (`/home/edgeai/edgeai`,
docroot `/home/edgeai/public_html`). **Тајна се не уписује у тај фајл** (он је у git-у):
чита се из `deploy/.env` на серверу, који је игнорисан у git-у и кога `deploy.sh` не брише.

```bash
cd ~/edgeai
cp deploy/.env.example deploy/.env && chmod 600 deploy/.env
# уреди deploy/.env: WEBHOOK_SECRET=$(openssl rand -hex 32)   (иста вредност иде у GitHub, корак 4)
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
| Secret | иста вредност као `WEBHOOK_SECRET` у `deploy/.env` на серверу |
| Events | Just the `push` event |

### 5. Прва објава

```bash
cd ~/edgeai && bash deploy/deploy.sh
```

Затим на GitHub-у: Webhooks → Recent Deliveries → **Redeliver** ping.

## Ротација тајне (и прелаз са старе верзије)

Старије верзије су имале `WEBHOOK_SECRET` уписан у `ecosystem.config.js` у git-у, па ту
вредност треба сматрати откривеном. Редослед да деплој не стане:

1. На серверу направи нову тајну и упиши је у `deploy/.env` (нови фајл, види горе).
2. `git pull`, па `pm2 restart edgeai-webhook --update-env`. Од ове верзије сервис
   **одбија да се покрене без тајне** и одбија сваки захтев без исправног потписа.
3. У GitHub → Settings → Webhooks промени **Secret** на ту исту нову вредност.
4. Проверај: Recent Deliveries → Redeliver → одговор `200`.

Између корака 2 и 3 push-еви ће добијати `401` — то је очекивано и траје само док не промениш тајну на GitHub-у.

## Свакодневно

Само `git push` у `main`. Ако push дира `web/**` → сајт се сам преведе и објави
за ~1 минут. Логови: `deploy/logs/webhook.log` и `deploy/logs/deploy.log`.

Ручни deploy у нужди: `bash ~/edgeai/deploy/deploy.sh`.

## Потребно на серверу

`node` (18+), `npm`, `git`, `bash`, `rsync`, `pm2`. Node се у Virtualmin-у
добија преко EasyApache/„Node.js“ или `nvm`.
