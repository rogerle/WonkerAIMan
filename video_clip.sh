#!/bin/bash

set -e
source path.sh

python ${UTILS_DIR}/preprocess_util/video_resize.py --data_root=data/lip_src/ \
                                                         --ngpu=1