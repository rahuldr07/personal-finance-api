.PHONY: install run test lint seed smoke

install:
	python3 -m pip install -e ".[dev]"

run:
	uvicorn finance_api.main:app --reload

test:
	pytest

lint:
	ruff check .

seed:
	python3 scripts/seed_demo.py

smoke:
	curl http://127.0.0.1:8000/health
