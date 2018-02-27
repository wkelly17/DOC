#!/usr/bin/env bash

# Download latest catalog
wget https://api.unfoldingword.org/uw/txt/2/catalog.json
mkdir -p /var/www/vhosts/api.unfoldingword.org/httpdocs/uw/txt/2
mv catalog.json /var/www/vhosts/api.unfoldingword.org/httpdocs/uw/txt/2

# Call pdf_export with passed parameters
./uwb/bible/pdf_export.sh "$@"
