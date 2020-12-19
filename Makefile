build:
	docker-compose build

up:
	docker-compose up -d

server: up
	docker-compose run  api

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration /tests/e2e
	# docker-compose run --rm --no-deps --entrypoint=pytest api  /tests/e2e

unit-tests:
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit

integration-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration

e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e

down:
	docker-compose down --remove-orphans

stubgen:
	stubgen src/document/domain/resource.py
	stubgen src/document/domain/document_generator.py
	stubgen src/document/domain/resource_lookup.py
	stubgen src/document/domain/bible_books.py
	stubgen src/document/entrypoints/app.py
	stubgen src/document/utils/file_utils.py
	stubgen src/document/utils/url_utils.py

all: down build up test
