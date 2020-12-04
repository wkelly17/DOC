#!/usr/bin/env bash
export FLASK_APP=./src/document/entrypoints/flask_app.py
export FLASK_RUN_HOST=localhost
export FLASK_RUN_PORT=5005
export FLASK_DEBUG=1
export IN_CONTAINER=
export IRG_WORKING_DIR=./working/temp
flask run
