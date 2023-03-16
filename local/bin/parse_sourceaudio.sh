#!/bin/bash
##这个脚本用来预处理声音，对于
set -e
source path.sh
export UTIL_DIR=${MAIN_ROOT}/local/utils


#执行音频文件处理
  python ${UTIL_DIR}/parse_audio.py \
            --input_dir=data/source \
            --output_dir=output