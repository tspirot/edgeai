---
name: deploy
description: Deploy the Edge AI site (web/) to edgeai.tsp.edu.rs on Virtualmin. Use when asked to deploy, publish, push the site live, or update the subdomain.
---

# Deploy сајта на edgeai.tsp.edu.rs

Сервер: Virtualmin (Apache), поддомен `edgeai.tsp.edu.rs`.
Document root (потврди у Virtualmin-у): `~/domains/edgeai.tsp.edu.rs/public_html`.

Постоје два начина. **Подразумевани је GitHub Actions** (билд у облаку, деплој преко SSH).

## 1. GitHub Actions (препоручено)

Workflow је `.github/workflows/deploy.yml`. Окида се на push у `main` који мења `web/**`.

Потребне GitHub тајне (Settings → Secrets → Actions):

| тајна | вредност |
|---|---|
| `SSH_HOST` | нпр. `tsp.edu.rs` |
| `SSH_USER` | Virtualmin корисник домена |
| `SSH_KEY` | приватни SSH кључ (деплој кључ) |
| `SSH_PORT` | најчешће `22` |
| `DEPLOY_PATH` | `/home/<user>/domains/edgeai.tsp.edu.rs/public_html` |

Ручно покретање: **Actions → Deloy site → Run workflow**.

## 2. Webhook на серверу (алтернатива, ако нема Actions)

Скрипта `deploy/webhook.php` и `deploy/deploy.sh` (види `deploy/README.md`).
Тражи Node.js на серверу. У Virtualmin-у: **Webmin → Others → нема**;
webhook се поставља као PHP скрипта + GitHub webhook (Settings → Webhooks),
Content-type `application/json`, Secret = вредност `WEBHOOK_SECRET` из `deploy/.env`.

## Ручни деплој (у нужди)

```bash
cd web
npm ci
npm run build
rsync -avz --delete dist/ <user>@tsp.edu.rs:/home/<user>/domains/edgeai.tsp.edu.rs/public_html/
```

`web/public/.htaccess` се копира у `dist/` при билду и решава SPA рутирање — не брисати.

## Провера после деплоја

- `https://edgeai.tsp.edu.rs/` се учитава, 3D сцена ради.
- Директан улаз на `https://edgeai.tsp.edu.rs/projekti/titlovi-uzivo` не даје 404 (значи `.htaccess` ради).
- У прегледачу нема грешака у конзоли.
