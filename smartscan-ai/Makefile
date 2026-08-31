.PHONY: install backend frontend test lint validate benchmark demo check

install:
	pip install -e .[dev]

backend:
	uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

frontend:
	npm run dev --prefix frontend

test:
	pytest tests/

lint:
	black .
	flake8 .

validate:
	python scripts/validate_data.py

benchmark:
	python scripts/run_benchmarks.py

demo:
	python scripts/run_demo.py

check: lint test validate
