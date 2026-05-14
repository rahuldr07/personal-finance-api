# Development Guide

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

## Run

```bash
uvicorn finance_api.main:app --reload
```

## Test

```bash
pytest
```

## Lint

```bash
ruff check .
```

## Smoke Test

After starting the API, verify the health endpoint:

```bash
curl http://127.0.0.1:8000/health
```
