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
	@pip install pip-tools
endif

ifeq ("$(wildcard .venv/bin/pip-sync)","")
	@echo "Installing Pip-tools..."
	@pip install pip-tools
endif

.PHONY: build
build: checkvenv local-update-deps-dev
	docker-compose build

.PHONY: build-no-cache
build-no-cache: checkvenv
	docker-compose build --no-cache

.PHONY: up
up: checkvenv
	docker-compose up -d

.PHONY: server
server: up
	docker-compose run  api

.PHONY: test
test: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration /tests/e2e

.PHONY: unit-tests
unit-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit

.PHONY: integration-tests
integration-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration

.PHONY: e2e-tests
e2e-tests: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e

.PHONY: down
down:
	docker-compose down --remove-orphans

.PHONY: mypy-install-types
mypy-install-types: checkvenv
	mypy --install-types --non-interactive  # install all missing stub packages

.PHONY: mypy
mypy: mypy-install-types
	mypy --strict src/document/*.py
	mypy --strict src/document/**/*.py
	mypy --strict tests/*.py
	mypy --strict tests/**/*.py

.PHONY: pyicontract-lint
pyicontract-lint: checkvenv
	pyicontract-lint --dont_panic src/document/domain
	pyicontract-lint --dont_panic src/document/utils
	pyicontract-lint --dont_panic src/document/entrypoints

# https://radon.readthedocs.io/en/latest/commandline.html
.PHONY: radon-cyclomatic-complexity
radon-cyclomatic-complexity: checkvenv
	radon cc src/document/**/*.py

.PHONY: radon-raw-stats
radon-raw-stats: checkvenv
	radon raw src/document/**/*.py

.PHONY: radon-maintainability-index
radon-maintainability-index: checkvenv
	radon mi src/document/**/*.py

.PHONY: radon-halstead-complexity
radon-halstead-complexity: checkvenv
	radon hal src/document/**/*.py

.PHONY: vulture-dead-code
vulture-dead-code: checkvenv
	vulture src/document/ --min-confidence 100
	vulture tests/ --min-confidence 100

.PHONY: all
all: down build up test

.PHONY: all-plus-linting
all-plus-linting: mypy pyicontract-lint down build up test

#########################
# Local dev

# Run a local Uvicorn server outside Docker
.PHONY: local-uvicorn-server
local-server: checkvenv
	uvicorn document.entrypoints.app:app --reload --host "127.0.0.1" --port "5005" --app-dir "./src/"

.PHONY: local-gunicorn-server
local-gunicorn-server: checkvenv
	exec gunicorn --name IRG --worker-class uvicorn.workers.UvicornWorker --conf ./gunicorn.conf.py --pythonpath ./src  document.entrypoints.app:app

.PHONY: local-update-deps-prod
local-update-deps-prod: checkvenv
	pip-compile # --upgrade

.PHONY: local-update-deps-dev
local-update-deps-dev: local-update-deps-prod
	pip-compile requirements-dev.in
	# pip-compile --upgrade requirements-dev.in

.PHONY: local-install-deps-prod
local-install-deps-prod: local-update-deps-prod
	pip install -r requirements.txt

.PHONY: local-install-deps-dev
local-install-deps-dev: local-update-deps-dev
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

.PHONY: local-prepare-for-tests
local-prepare-for-tests: mypy pyicontract-lint local-clean-working-output-dir

.PHONY: local-prepare-for-tests-without-cleaning
local-prepare-for-tests-without-cleaning: mypy pyicontract-lint

.PHONY: local-clean-working-output-dir
local-clean-working-output-dir:
	find working/output/ -type f -name "*.html" -exec rm -- {} +
	find working/output/ -type f -name "*.pdf" -exec rm -- {} +

# local-unit-tests: local-install-deps-dev local-prepare-for-tests
.PHONY: local-unit-tests
local-unit-tests:  local-prepare-for-tests-without-cleaning
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/unit/ -vv

# local-e2e-tests: local-install-deps-dev local-prepare-for-tests
.PHONY: local-e2e-tests
local-e2e-tests:  local-prepare-for-tests-without-cleaning
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -vv

.PHONY: local-smoke-test-with-translation-words
local-smoke-test-with-translation-words: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order

.PHONY: local-smoke-test-with-translation-words2
local-smoke-test-with-translation-words2: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_rom_en_tn_wa_rom_en_tq_wa_rom_en_tw_wa_rom_es_419_ulb_rom_es_419_tn_rom_en_tq_rom_es_419_tw_rom_book_language_order

.PHONY: local-icontract-hypothesis-tests
local-icontract-hypothesis-tests: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pyicontract-hypothesis test -p src/document/domain/resource.py

.PHONY: local-icontract-hypothesis-test2
local-icontract-hypothesis-tests2: local-prepare-for-tests
	IN_CONTAINER=false ENABLE_ASSET_CACHING=true SEND_EMAIL=false FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pyicontract-hypothesis test -p src/document/entrypoints/app.py

# This is one to run after running local-e2e-tests or any tests which
# has yielded HTML and PDFs that need to be checked for linking
# correctness.
.PHONY: local-check-anchor-links
local-check-anchor-links: checkvenv
	IN_CONTAINER=false python tests/e2e/test_anchor_linking.py
