.PHONY: install run test lint seed

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

