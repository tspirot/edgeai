# Deploy на edgeai.tsp.edu.rs (Virtualmin)

Два начина. Изабери један.

---

## A) GitHub Actions (препоручено)

Билд се ради на GitHub-у, готов `dist/` се преко `rsync`/SSH пребаци на сервер.
Сервер не мора да има Node.js.

### 1. Направи деплој SSH кључ (на свом рачунару)

```bash
ssh-keygen -t ed25519 -f edgeai_deploy -N "" -C "github-actions-edgeai"
```

### 2. Јавни кључ на сервер

У Virtualmin-у за корисника домена: **SSH Keys → додај садржај `edgeai_deploy.pub`**,
или ручно у `~/.ssh/authorized_keys`.

### 3. GitHub тајне

Repo **Settings → Secrets and variables → Actions → New repository secret**:

| тајна | пример |
|---|---|
| `SSH_HOST` | `tsp.edu.rs` |
| `SSH_USER` | Virtualmin корисник домена (нпр. `edgeai`) |
| `SSH_PORT` | `22` |
| `SSH_KEY` | цео садржај приватног `edgeai_deploy` |
| `DEPLOY_PATH` | `/home/edgeai/domains/edgeai.tsp.edu.rs/public_html` |

### 4. Готово

Сваки push у `main` који дира `web/**` покреће **Actions → Deploy site**.
Ручно: Actions → Deploy site → **Run workflow**.

---

## B) Webhook на серверу

Сервер повуче репо и сам изгради сајт. **Тражи Node.js на серверу**
(Virtualmin: EasyApache/Node, или `nvm`).

### 1. Клонирај репо на сервер (једном)

```bash
cd ~
git clone https://github.com/tspirot/edgeai.git
```

### 2. Подеси deploy/.env

```bash
cd ~/edgeai/deploy
cp .env.example .env
nano .env        # WEBHOOK_SECRET (насумичан низ), REPO_DIR, PUBLIC_HTML
chmod +x deploy.sh
```

### 3. Изложи webhook.php

Најлакше: копирај `webhook.php` у `public_html/` (остаје у истом фолдеру као
`.env` и `deploy.sh` — стави их једно ниво изнад и промени путање, или све у
`public_html` па заштити `.env`):

```apache
# .htaccess у public_html
<Files ".env">
  Require all denied
</Files>
<Files "deploy.sh">
  Require all denied
</Files>
```

### 4. GitHub webhook

Repo **Settings → Webhooks → Add webhook**:

- Payload URL: `https://edgeai.tsp.edu.rs/webhook.php`
- Content type: `application/json`
- Secret: иста вредност као `WEBHOOK_SECRET`
- Events: **Just the push event**

Провера: GitHub прикаже „✔ ping“ · `deploy/last-deploy.log` на серверу показује ток.

---

## Ручни деплој (у нужди, без ичега)

```bash
cd web && npm ci && npm run build
rsync -avz --delete web/dist/ USER@HOST:/.../public_html/
```

`web/public/.htaccess` → копира се у `dist/` и решава SPA рутирање. Не брисати.
