# Edge AI: Наука у петој брзини

Монорепо програма **„Edge AI: Наука у петој брзини“** Техничке школе Пирот —
вештачка интелигенција која ради на самом уређају, без облака.

Сајт: **[edgeai.tsp.edu.rs](https://edgeai.tsp.edu.rs)**

## Структура

| путања | шта је |
|---|---|
| `web/` | сајт (React + Vite + react-three-fiber) — пројекти, упутства, 3D насловна |
| `lms/primeri/` | примери за Raspberry Pi 5 (Python) — вежбе уз лекције на страни `/lms` |
| `projekti/` | 12 ученичких пројеката (Python, свако са својим `README.md`, `pyproject.toml` и тестовима): `titlovi-uzivo`, `pametna-zebra`, `cuvar-stare-planine`, `kontrola-kvaliteta`, `znakovna-azbuka`, `skolski-asistent`, `djak-za-volanom`, `hodnik-u-glavi`, `uspravno`, `pirotski-cilim`, `dvojnik`, `ziva-rec` |
| `docs/` | документација и нацрти, укључујући `privatnost.md` (правила за податке ученика) |
| `deploy/` | webhook deploy на Virtualmin (Node сервис + PM2 + `deploy.sh`) |
| `.github/workflows/` | CI: провера билда сајта и тестова пројеката |
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

## Лиценца и извори

* Кôд: [MIT](LICENSE).
* Садржај сајта, упутства и лекције: [CC BY-SA 4.0](LICENSE-CONTENT).
* Материјал трећих страна и отворена питања лиценце: [CREDITS.md](CREDITS.md).
* Пријава безбедносних проблема: [SECURITY.md](SECURITY.md). Како допринети: [CONTRIBUTING.md](CONTRIBUTING.md).
* Подаци ученика (камера, глас): [docs/privatnost.md](docs/privatnost.md).
