app = "src.productizer.main:app"
puluni_stack = "virtualfinland/dev"

install:
	python -m pip install poetry poetry-dotenv-plugin
	python -m poetry config virtualenvs.in-project true
	python -m poetry install
run:
	python -m poetry run uvicorn --host 0.0.0.0 ${app}
dev:
	python -m poetry run uvicorn --reload --host 0.0.0.0 ${app}
test:
	python -m poetry run pytest
lint:
	python -m poetry run black ./src/productizer
lint-check:
	python -m poetry run black ./src/productizer --check
build:
	python -m poetry build
clean:
	rm -rf .venv
	rm -rf ./infra/.lambda
build-for-pulumi:
	mkdir -p ./infra/.lambda
	python -m poetry export --without-hashes -f requirements.txt --output ./infra/.lambda/requirements.txt
	python -m pip install -r ./infra/.lambda/requirements.txt -t ./infra/.lambda/layer
init-pulumi: build-for-pulumi
	python -m poetry run pulumi --cwd ./infra stack select ${puluni_stack} || poetry run pulumi --cwd ./infra stack init ${puluni_stack}
deploy-pulumi: init-pulumi
	python -m poetry run pulumi --cwd ./infra --non-interactive up --yes
deploy-pulumi-preview: init-pulumi
	python -m poetry run pulumi --cwd ./infra --non-interactive preview 