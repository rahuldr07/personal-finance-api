# Personal Finance API

A polished FastAPI backend for tracking personal expenses, budgets, recurring bills, and spending
insights. The project is intentionally small enough to run locally, but it uses the same building
blocks expected in a production-style backend: authentication, database persistence, validation,
tests, CLI tooling, Docker support, and developer documentation.

## Highlights

```text
Auth + JWT        Expense CRUD       Budget tracking
CSV export        CLI workflow       Recurring bills
Savings goals     Insights API       Dashboard summary
Docker setup      Test coverage      Rich filters
```

## What It Does

- Registers users and issues JWT bearer tokens
- Tracks expenses with categories, dates, notes, and amount filters
- Supports expense search, updates, deletes, and CSV export
- Manages monthly category budgets
- Tracks recurring expenses such as subscriptions, rent, bills, and memberships
- Tracks payment method and merchant details for cleaner expense history
- Tracks savings goals with progress and remaining amount
- Reports monthly totals, yearly totals, top expenses, category share, insights, and budget status
- Provides a compact dashboard summary for monthly account health
- Provides a CLI client for common local workflows
- Runs with SQLite by default for quick setup

## Tech Stack

- **API:** FastAPI
- **Database:** SQLite with SQLAlchemy
- **Validation:** Pydantic
- **Auth:** JWT tokens with Passlib password hashing
- **CLI:** Typer and HTTPX
- **Testing:** Pytest and FastAPI TestClient
- **Quality:** Ruff
- **Packaging:** `pyproject.toml`

## Project Layout

```text
.
├── src/
│   ├── finance_api/      # FastAPI app, routers, schemas, services, database models
│   └── finance_cli/      # CLI client for the API
├── tests/                # API test coverage
├── docs/                 # API, security, and development notes
├── scripts/              # Local helper scripts
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

## Requirements

- Python 3.11 or newer
- Git
- Optional: Docker and Docker Compose

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn finance_api.main:app --reload
```

Open the interactive API docs:

```text
http://127.0.0.1:8000/docs
```

Health check:

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{"status":"ok","version":"0.1.0"}
```

## Environment

Copy `.env.example` to `.env` before running locally.

```env
APP_NAME=Personal Finance API
DATABASE_URL=sqlite:///./finance.db
SECRET_KEY=change-this-local-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Use a unique `SECRET_KEY` outside local development.

## API Workflow

Register a user:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@example.com","password":"password123"}'
```

Log in:

```bash
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=dev@example.com&password=password123"
```

Create an expense:

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Lunch","amount":12.5,"category":"food","spent_on":"2026-05-17"}'
```

Get monthly spending:

```bash
curl "http://127.0.0.1:8000/reports/monthly?year=2026&month=5" \
  -H "Authorization: Bearer <TOKEN>"
```

## CLI Usage

After the API is running:

```bash
finance-cli register dev@example.com password123
finance-cli login dev@example.com password123
finance-cli add "Lunch" 12.5 food 2026-05-17
finance-cli add "Headphones" 80 shopping 2026-05-17 "" credit_card "Audio Store"
finance-cli list --category food
finance-cli summary 2026 5
finance-cli dashboard 2026 5
finance-cli budget-add food 500
finance-cli budget-status 2026 5
finance-cli goal-add "Emergency fund" 1000 250
finance-cli goal-list
finance-cli recurring-add "Internet bill" 49.99 bills monthly 2026-06-01
finance-cli recurring-list
finance-cli insights 2026 5
finance-cli export --output expenses.csv
```

Override the API URL if needed:

```bash
FINANCE_API_URL=http://127.0.0.1:9000 finance-cli list
```

## Developer Commands

```bash
make install
make run
make test
make lint
make seed
```

Equivalent direct commands:

```bash
pytest
ruff check .
python3 scripts/seed_demo.py
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

The API will be available at:

```text
http://127.0.0.1:8000
```

## Main Endpoints

| Area | Endpoint |
| --- | --- |
| Health | `GET /health` |
| Auth | `POST /auth/register`, `POST /auth/login`, `GET /auth/me` |
| Expenses | `POST /expenses`, `GET /expenses`, `GET /expenses/{id}` |
| Expenses | `PATCH /expenses/{id}`, `DELETE /expenses/{id}` |
| Budgets | `POST /budgets`, `GET /budgets`, `PATCH /budgets/{id}` |
| Budgets | `DELETE /budgets/{id}`, `GET /budgets/status/monthly` |
| Recurring | `POST /recurring-expenses`, `GET /recurring-expenses` |
| Recurring | `PATCH /recurring-expenses/{id}`, `DELETE /recurring-expenses/{id}` |
| Reports | `GET /reports/monthly`, `GET /reports/yearly` |
| Reports | `GET /reports/top-expenses`, `GET /reports/category-shares` |
| Reports | `GET /reports/insights` |
| Export | `GET /reports/export.csv` |

## Example Insight Response

```json
{
  "expense_count": 8,
  "total_spent": 942.35,
  "average_expense": 117.79,
  "largest_expense": 400.0,
  "highest_category": "bills"
}
```

## Troubleshooting

### `python: command not found`

Use `python3` instead:

```bash
python3 -m venv .venv
```

### Login fails after changing `.env`

Restart the API. JWT settings are loaded when the application starts.

### Database has old test data

Delete the local SQLite file and restart:

```bash
rm -f finance.db
uvicorn finance_api.main:app --reload
```

### CLI says to log in first

Run:

```bash
finance-cli login dev@example.com password123
```

## Quality Status

The project is expected to pass:

```bash
pytest
ruff check .
```
