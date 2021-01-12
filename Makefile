build:
	docker-compose build

up:
	docker-compose up -d

server: up
	docker-compose run  api

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration /tests/e2e

unit-tests:
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e

down:
	docker-compose down --remove-orphans

mypy:
	mypy src/document/*.py
	mypy src/document/**/*.py
	mypy tests/*.py
	mypy tests/**/*.py

all: down build up test
