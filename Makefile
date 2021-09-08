build: local-update-deps-dev # use-stable-translations-json
	docker-compose build

build-no-cache: # use-stable-translations-json
	docker-compose build --no-cache

up:
	docker-compose up -d

# Deal with instability with upstream translations.json
use-stable-translations-json:
	git checkout working/temp/translations.json
	touch working/temp/translations.json
# ifeq ($(TRANSLATIONS_JSON_FROM_GIT),1)
# 	git checkout working/temp/translations.json
# 	touch working/temp/translations.json
# else
# 	rm working/temp/translations.json
# endif

server: up
	docker-compose run  api

# Run a local server outside Docker
local-server:
	uvicorn document.entrypoints.app:app --reload --host "127.0.0.1" --port "5005" --app-dir "./src/"

test: up
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit /tests/integration /tests/e2e

unit-tests: up # use-stable-translations-json
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/unit

integration-tests: up # use-stable-translations-json
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/integration

e2e-tests: up # use-stable-translations-json
	docker-compose run --rm --no-deps --entrypoint=pytest api /tests/e2e

down:
	docker-compose down --remove-orphans

mypy:
	mypy --install-types # install all missing stub packages
	mypy src/document/*.py
	mypy src/document/**/*.py
	mypy tests/*.py
	mypy tests/**/*.py

pyicontract-lint:
	pyicontract-lint --dont_panic src/document/domain
	pyicontract-lint --dont_panic src/document/utils
	pyicontract-lint --dont_panic src/document/entrypoints

# https://radon.readthedocs.io/en/latest/commandline.html
radon-cyclomatic-complexity:
	radon cc src/document/**/*.py

radon-raw-stats:
	radon raw src/document/**/*.py

radon-maintainability-index:
	radon mi src/document/**/*.py

radon-halstead-complexity:
	radon hal src/document/**/*.py

all: down build up test

all-plus-linting: mypy pyicontract-lint down build up test

#########################
# Local dev

# Just for documentation
# init:
# 	python3 -m venv venv
# 	pip install pip-tools

# Just for documentation, doesn't work
# venv-bash-shell:
# 	source venv/bin/activate

# Just for documentation, doesn't work
# venv-fish-shell:
# 	fish -c deactivate
# 	source venv/bin/activate.fish

local-update-deps-prod:
	pip-compile --upgrade

local-update-deps-dev: local-update-deps-prod
	pip-compile --upgrade requirements-dev.in

pip-warning:
	echo "If you aren't in your virtual env shell, source venv/bin/activate, then this will install into global package index"

local-install-deps-prod: local-update-deps-prod pip-warning
	pip install -r requirements.txt

local-install-deps-dev: local-update-deps-dev pip-warning
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

local-prepare-for-tests: mypy pyicontract-lint local-clean-working-output-dir # use-stable-translations-json

local-prepare-for-tests-without-cleaning: mypy pyicontract-lint  # use-stable-translations-json

local-clean-working-output-dir:
	find working/output/ -type f -name "*.html" -exec rm -- {} +
	find working/output/ -type f -name "*.pdf" -exec rm -- {} +

# local-unit-tests: local-install-deps-dev local-prepare-for-tests
local-unit-tests:  local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/unit/ -vv

# local-e2e-tests: local-install-deps-dev local-prepare-for-tests
local-e2e-tests:  local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -vv

# Run one quick test
local-smoke-test: local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_send_email_with_ar_nav_jud_pdf

# Test case chosen does not pass email with document request.
local-smoke-test-with-no-email: local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_language_book_order_with_no_email

local-smoke-test-with-translation-words: local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pytest tests/e2e/ -k test_en_ulb_wa_col_en_tn_wa_col_en_tq_wa_col_en_tw_wa_col_pt_br_ulb_col_pt_br_tn_col_pt_br_tq_col_pt_br_tw_col_book_language_order

local-icontract-hypothesis-tests: local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pyicontract-hypothesis test -p src/document/domain/resource.py

local-icontract-hypothesis-tests2: local-prepare-for-tests
	ENABLE_ASSET_CACHING=1 TRANSLATIONS_JSON_FROM_GIT=1 SEND_EMAIL=0 FROM_EMAIL="foo@example.com" TO_EMAIL="foo@example.com" pyicontract-hypothesis test -p src/document/entrypoints/app.py

local-email-tests: local-prepare-for-tests
	./test_email_DO_NOT_COMMIT.sh

# This is one to run after running local-e2e-tests or
# local-smoke-test-with-translation-words
local-check-anchor-links:
	python tests/e2e/test_anchor_linking.py
