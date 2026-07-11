.PHONY: install test run-streamlit run-fastapi clean lint

install:
	pip install -r requirements.txt
	pip install -e .

test:
	pytest tests/ --cov=src --cov-report=term-missing

run-streamlit:
	streamlit run app.py

run-fastapi:
	uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

lint:
	black --check src/ tests/
	flake8 src/ tests/ || true

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov .venv
	find . -type d -name "__pycache__" -exec rm -r {} +
