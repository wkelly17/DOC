#!/usr/bin/env bash
rm -rf ./working/temp/*
git restore working/temp/icon-tn.png
git restore working/temp/keepme.txt
python -m tests.test_resource_lookup
# echo "Prettifying downloaded translations.json for easier investigation"
# prettier -w working/temp/translations.json
