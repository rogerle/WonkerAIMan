#!/bin/bash

set -e
source path.sh
export UTIL_DIR=${MAIN_ROOT}/local/utils

python  ${UTIL_DIR}/py.py --content_txt=output/LJ_Voice/content.txt \
              --labels_txt=output/LJ_Voice/labels.txt


