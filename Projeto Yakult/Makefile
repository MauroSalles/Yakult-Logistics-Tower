.PHONY: run test lint format install clean

## Install production + dev dependencies
install:
	pip install -r requirements.txt

## Run the Streamlit dashboard
run:
	streamlit run app_logistica.py

## Run the test suite
test:
	python -m pytest

## Lint the code base (read-only)
lint:
	python -m ruff check .

## Auto-format the code base
format:
	python -m ruff format .
	python -m ruff check --fix .

## Remove caches
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	rm -rf .pytest_cache .ruff_cache
