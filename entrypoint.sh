#!/usr/bin/env bash

# Run server
uvicorn --host 0.0.0.0 --port 5005 --reload document.entrypoints.app:app
