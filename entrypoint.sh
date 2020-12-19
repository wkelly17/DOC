#!/usr/bin/env bash

# Combine OT and NT tW files into single refs file, skipping header row of NT
# cp         /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_OT_PDF.txt    /working/tn-temp/tw_refs.csv
# tail -n +2 /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_NT_PDF.txt >> /working/tn-temp/tw_refs.csv

# Copy images
# cp /working/*.png /working/temp

# Run server
uvicorn --host 0.0.0.0 --port 5005 --reload src.document.entrypoints.app:app
