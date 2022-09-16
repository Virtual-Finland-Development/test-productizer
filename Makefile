app = "productizer.main:app"
puluni-stack = "virtualfinland/dev"

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
	python -m poetry run black ./productizer
lint-check:
	python -m poetry run black ./productizer --check
build:
	python -m poetry build
clean:
	rm -rf .venv
	rm -rf ./pulumi/.lambda
set-region:
	python -m poetry run pulumi --cwd ./pulumi config set aws:region ${AWS_REGION}
	python -m poetry run pulumi --cwd ./pulumi config set aws-native:region ${AWS_REGION}
build-for-pulumi:
	mkdir -p ./pulumi/.lambda
	python -m poetry export --without-hashes -f requirements.txt --output ./pulumi/.lambda/requirements.txt
	python -m pip install -r ./pulumi/.lambda/requirements.txt -t ./pulumi/.lambda/layer
init-pulumi: build-for-pulumi
	python -m poetry run pulumi --cwd ./pulumi stack select ${puluni-stack} || poetry run pulumi --cwd ./pulumi stack init ${puluni-stack}
deploy-pulumi: init-pulumi
	python -m poetry run pulumi --cwd ./pulumi --non-interactive up --yes
deploy-pulumi-preview: init-pulumi
	python -m poetry run pulumi --cwd ./pulumi --non-interactive preview 