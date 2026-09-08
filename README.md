# Edge AI Пирот

Монорепо програма **Edge AI** Техничке школе Пирот — вештачка интелигенција која
ради на самом уређају, без облака.

Сајт: **[edgeai.tsp.edu.rs](https://edgeai.tsp.edu.rs)**

## Структура

| путања | шта је |
|---|---|
| `web/` | сајт (React + Vite + react-three-fiber) — пројекти, упутства, 3D насловна |
| `projekti/titlovi-uzivo/` | „Титлови уживо“ — препознавање говора на српском на уређају (Python) |
| `deploy/` | deploy на Virtualmin (webhook + скрипте) |
| `.github/workflows/` | GitHub Actions: билд и deploy сајта |
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

Push у `main` који дира `web/**` → GitHub Actions билдује и објављује на
`edgeai.tsp.edu.rs`. Детаљи и алтернатива (webhook на серверу): `deploy/README.md`.

## Лиценца

Кôд: MIT. Садржај сајта и упутства: CC BY-SA 4.0.
