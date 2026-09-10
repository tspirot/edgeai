# Edge AI: Наука у петој брзини

Монорепо програма **„Edge AI: Наука у петој брзини“** Техничке школе Пирот —
вештачка интелигенција која ради на самом уређају, без облака.

Сајт: **[edgeai.tsp.edu.rs](https://edgeai.tsp.edu.rs)**

## Структура

| путања | шта је |
|---|---|
| `web/` | сајт (React + Vite + react-three-fiber) — пројекти, упутства, 3D насловна |
| `projekti/titlovi-uzivo/` | „Титлови уживо“ — препознавање говора на српском на уређају (Python) |
| `deploy/` | webhook deploy на Virtualmin (Node сервис + PM2 + `deploy.sh`) |
| `.github/workflows/` | CI: провера билда сајта и тестова |
| `.claude/skills/` | пројектни skill-ови за Claude Code |

## Брзо

```bash
# сајт
cd web && npm install && npm run dev        # http://localhost:5173

# титлови уживо
cd projekti/titlovi-uzivo
python -m venv .venv && source .venv/Scripts/activate
pip install -e ".[dev]" && pytest
```

VS Code: **Run and Debug** има готове конфигурације за сајт и за Python пројекат.

## Деплој

`git push` у `main` → GitHub webhook → Node сервис (PM2) на серверу преведе и
објави сајт на `edgeai.tsp.edu.rs` за ~1 минут (rollback ако build падне).
Поставка и решавање проблема: `deploy/README.md`.

## Лиценца

Кôд: MIT. Садржај сајта и упутства: CC BY-SA 4.0.
