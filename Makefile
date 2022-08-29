app = "productizer.main:app"

install:
	python -m pip install poetry
	poetry config virtualenvs.in-project true
	poetry install
run:
	poetry run uvicorn --host 0.0.0.0 ${app}
dev:
	poetry run uvicorn --reload --host 0.0.0.0 ${app}
test:
	poetry run pytest
lint:
	poetry run black ./productizer --check