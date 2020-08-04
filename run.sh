#!/usr/bin/env bash
#
#  Copyright (c) 2017 unfoldingWord
#  http://creativecommons.org/licenses/MIT/
#  See LICENSE file for details.
#
#  Contributors:
#  Richard Mahn <richard_mahn@wyciffeassociates.org>

cd $(dirname "$0")/..
python -m tools.export_md_to_pdf $@
