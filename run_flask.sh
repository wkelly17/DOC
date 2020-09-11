#!/usr/bin/env bash
export FLASK_APP=./flask_app.py
export FLASK_RUN_HOST=localhost
export FLASK_RUN_PORT=5005
export FLASK_DEBUG=1
flask run
