# Personal Finance API

A private FastAPI project for tracking personal expenses, reviewing category totals, and
testing backend development workflows.

## Features

- User registration and JWT login
- Expense create, list, update, and delete endpoints
- Category and date filters
- Monthly reports grouped by category
- Small CLI client for common actions
- SQLite local persistence
- Tests and Docker support

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn finance_api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API docs.

## Test

```bash
pytest
```

## Project Structure

- `src/finance_api/` contains the FastAPI backend.
- `src/finance_cli/` contains the CLI client.
- `tests/` contains API tests.
- `docs/` contains development and API notes.
