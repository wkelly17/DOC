.PHONY: checkvenv
checkvenv:
# raises error if environment is not active
ifeq ("$(VIRTUAL_ENV)","")
	@echo "Venv is not activated!"
	@echo "Activate venv first."
	@echo
	exit 1
endif

.PHONY: pyupgrade
pyupgrade: checkvenv
# checks if pip-tools is installed
ifeq ("$(wildcard .venv/bin/pip-compile)","")
	@echo "Installing Pip-tools..."
	@pip install --no-cache-dir pip-tools
endif

ifeq ("$(wildcard .venv/bin/pip-sync)","")
	@echo "Installing Pip-tools..."
	@pip install --no-cache-dir pip-tools
endif

.PHONY: build
build: checkvenv local-update-deps-prod
	docker-compose build

.PHONY: build-no-cache
build-no-cache: checkvenv
	docker-compose build --no-cache

.PHONY: up
up: checkvenv
	docker-compose up -d --force-recreate

# This runs just the backend
.PHONY: server
server: up
	docker-compose run backend

# This runs both the backend and the frontend
.PHONY: frontend-server
frontend-server: up
	docker-compose run frontend

.PHONY: test
test: up
	docker-compose run --rm --no-deps --entrypoint=pytest backend /tests/unit /tests/integration /tests/e2e

.PHONY: unit-tests
unit-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest backend /tests/unit

.PHONY: e2e-tests
e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest backend /tests/e2e

.PHONY: down
down:
	docker-compose down --remove-orphans

.PHONY: stop-and-remove
stop-and-remove:
	docker ps -q | xargs docker stop
	docker ps -a -q -f status=exited | xargs docker rm

.PHONY: mypy
mypy: checkvenv
	mypy --strict --install-types --non-interactive backend/document/**/*.py
	mypy --strict --install-types --non-interactive tests/**/*.py

.PHONY: mypyc
mypyc:
	mypyc --strict --install-types --non-interactive backend/document/**/*.py

# https://radon.readthedocs.io/en/latest/commandline.html
.PHONY: radon-cyclomatic-complexity
radon-cyclomatic-complexity: checkvenv
	radon cc backend/document/**/*.py

.PHONY: radon-raw-stats
radon-raw-stats: checkvenv
	radon raw backend/document/**/*.py

.PHONY: radon-maintainability-index
radon-maintainability-index: checkvenv
	radon mi backend/document/**/*.py

.PHONY: radon-halstead-complexity
radon-halstead-complexity: checkvenv
	radon hal backend/document/**/*.py

.PHONY: vulture-dead-code
vulture-dead-code: checkvenv
	vulture backend/document/ --min-confidence 100
	vulture tests/ --min-confidence 100

.PHONY: all
all: down build up test

.PHONY: all-plus-linting
all-plus-linting: mypy down build up test

# Run a local Uvicorn server outside Docker
.PHONY: local-server
local-server: checkvenv
	IN_CONTAINER=false uvicorn document.entrypoints.app:app --reload --host "0.0.0.0" --port "5005" --app-dir "./backend/"

# Run a local Gunicorn server outside Docker
.PHONY: local-gunicorn-server
local-gunicorn-server: checkvenv
	exec gunicorn --name DOC --worker-class uvicorn.workers.UvicornWorker --conf ./backend/gunicorn.conf.py --pythonpath ./backend  document.entrypoints.app:app

.PHONY: local-update-deps-base
local-update-deps-base: checkvenv
	pip-compile ./backend/requirements.in
	# pip-compile --upgrade ./backend/requirements.in

.PHONY: local-update-deps-prod
local-update-deps-prod: local-update-deps-base
	pip-compile ./backend/requirements-prod.in
	# pip-compile --upgrade ./backend/requirements-prod.in

.PHONY: local-update-deps-dev
local-update-deps-dev: local-update-deps-base
	pip-compile ./backend/requirements-dev.in
	# pip-compile --upgrade ./backend/requirements-dev.in

.PHONY: local-install-deps-base
local-install-deps-base: local-update-deps-base
	pip install --no-cache-dir -r ./backend/requirements.txt

.PHONY: local-install-deps-dev
local-install-deps-dev: local-update-deps-dev
	pip install --no-cache-dir -r ./backend/requirements.txt
	pip install --no-cache-dir -r ./backend/requirements-dev.txt

.PHONY: local-install-deps-prod
local-install-deps-prod: local-update-deps-prod
	pip install --no-cache-dir -r ./backend/requirements.txt
	pip install --no-cache-dir -r ./backend/requirements-prod.txt

.PHONY: local-prepare-for-tests
local-prepare-for-tests: mypy  local-clean-working-output-dir

.PHONY: local-prepare-for-tests-without-cleaning
local-prepare-for-tests-without-cleaning: mypy

.PHONY: local-clean-working-output-dir
local-clean-working-output-dir:
	find working/output/ -type f -name "*.html" -exec rm -- {} +
	find working/output/ -type f -name "*.pdf" -exec rm -- {} +

.PHONY: local-unit-tests
local-unit-tests:  local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/unit/ -vv

.PHONY: local-e2e-tests
local-e2e-tests:  local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -vv

.PHONY: local-smoke-test-with-translation-words
local-smoke-test-with-translation-words: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order

.PHONY: local-smoke-test-with-translation-words2
local-smoke-test-with-translation-words2: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_rom_en_tn_wa_rom_en_tq_wa_rom_en_tw_wa_rom_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order

.PHONY: local-smoke-test-with-translation-words3
local-smoke-test-with-translation-words3: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_es_419_ulb_col_es_419_tn_col_es_419_tq_col_es_419_tw_col_language_book_order

# This is one to run after running local-e2e-tests or any tests which
# has yielded HTML and PDFs that need to be checked for linking
# correctness.
.PHONY: local-check-anchor-links
local-check-anchor-links: checkvenv
	IN_CONTAINER=false python tests/e2e/test_anchor_linking.py
