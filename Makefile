build:
	docker-compose build

build-no-cache:
	docker-compose build --no-cache

up:
	docker-compose up -d

# Deal with instability with upstream translations.json
use-stable-translations-json:
ifeq ($(TRANSLATIONS_JSON_FROM_GIT),1)
	git checkout working/temp/translations.json
	touch working/temp/translations.json
else
	rm working/temp/translations.json
endif

server: up
	docker-compose run  api

# Run a local server outside Docker
local-server:
	uvicorn document.entrypoints.app:app --reload --host "127.0.0.1" --port "8000" --app-dir "./src/"

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration /tests/e2e

unit-tests: up use-stable-translations-json
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit

integration-tests: up use-stable-translations-json
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration

e2e-tests: up use-stable-translations-json
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e

down:
	docker-compose down --remove-orphans

mypy:
	mypy src/document/*.py
	mypy src/document/**/*.py
	mypy tests/*.py
	mypy tests/**/*.py

pyicontract-lint:
	pyicontract-lint --dont_panic ./src/document/domain
	pyicontract-lint --dont_panic ./src/document/utils
	pyicontract-lint --dont_panic ./src/document/entrypoints

all: down build up test

all-plus-linting: mypy pyicontract-lint down build up test

#########################
# Local dev

# init:
# 	python3 -m venv venv
# 	pip install pip-tools

# venv-bash-shell:
# 	source venv/bin/activate

# venv-fish-shell:
# 	fish -c deactivate
# 	source venv/bin/activate.fish

local-update-deps:
	pip-compile --upgrade
	pip-compile --upgrade requirements-dev.in
	# pip-compile --upgrade --generate-hashes
	# pip-compile --upgrade --generate-hashes requirements-dev.in

pip-warning:
	RED='\033[0;31m'
	NC='\033[0m' # No Color
	echo -e "${RED}If you aren't in your virtual env shell, source venv/bin/activate, then this will install into global package index${NC} World"

local-install-deps-prod: local-update-deps pip-warning
	pip install -r requirements.txt
	# pip-sync

local-install-deps-dev: local-update-deps pip-warning
	pip install -r requirements.txt
	pip install -r requirements-dev.txt
	# pip-sync requirements.txt requirements-dev.txt

local-prepare-for-tests: mypy local-clean-working-temp-dir local-use-stable-translations-json

local-clean-working-temp-dir:
	find working/temp/ -type f -name "*.html" -exec rm -- {} +
	find working/temp/ -type f -name "*.pdf" -exec rm -- {} +

local-use-stable-translations-json:
	git checkout working/temp/translations.json

local-unit-tests: local-install-deps-dev local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/unit/

local-e2e-tests: local-install-deps-dev local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/

# Run one quick test
local-smoke-test: local-install-deps-dev local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_send_email_with_ar_nav_jud_pdf

local-email-tests: local-install-deps-dev local-prepare-for-tests
	./test_email_DO_NOT_COMMIT.sh
