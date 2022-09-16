include .env
app = "productizer.main:app"
puluni-stack = "virtualfinland/dev"

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
	poetry run black ./productizer
lint-check:
	poetry run black ./productizer --check
build:
	poetry build
build-for-pulumi:
	mkdir -p ./pulumi/.lambda
	poetry export --output ./pulumi/.lambda/requirements.txt
init-pulumi:
	poetry run pulumi --cwd ./pulumi stack select ${puluni-stack} || poetry run pulumi --cwd ./pulumi stack init ${puluni-stack}
	poetry run pulumi --cwd ./pulumi config set AUTHORIZATION_GW_ENDPOINT_URL $(AUTHORIZATION_GW_ENDPOINT_URL)
deploy-pulumi: init-pulumi
	poetry run pulumi --cwd ./pulumi up
deploy-pulumi-preview: init-pulumi
	poetry run pulumi --cwd ./pulumi preview