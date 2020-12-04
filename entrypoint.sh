#!/usr/bin/env bash

# Create repos from WA content
# REPOS=( "en_ulb" "en_udb" "en_tn" "en_tq" "en_tw" "en_ta" )
# for REPO in "${REPOS[@]}"
# do
#     cd /working/tn-temp
#     if [ ! -d ${REPO} ]; then
#         # Repo doesn't exist, create it
#         git clone --depth=1 ${IRG_CS_USER_URL}/${REPO}
#     else
#         # Repo exists, update it
#         cd ${REPO}
#         git pull
#     fi
# done

# Combine OT and NT tW files into single refs file, skipping header row of NT
# cp         /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_OT_PDF.txt    /working/tn-temp/tw_refs.csv
# tail -n +2 /working/tn-temp/en_tw/tWs_for_PDFs/tWs_for_NT_PDF.txt >> /working/tn-temp/tw_refs.csv

# Copy images
cp /working/*.png /working/temp

# Create PDFs

# python -m tools.export_md_to_pdf --working /working/tn-temp ${TN_ADDITIONAL_PARMS}
# python -m tools.document_generator --working /working/tn-temp ${TN_ADDITIONAL_PARMS}
flask run


# Zip up all PDFs into single archive
# zip -j /working/tn-temp/interleaved_tns.zip /working/tn-temp/*.pdf

# Write to output directory
# cp /working/tn-temp/*.pdf /output
# cp /working/tn-temp/*.zip /output
