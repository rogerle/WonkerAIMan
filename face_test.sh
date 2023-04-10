#!/bin/bash

set -e
source path.sh

python ${UTILS_DIR}/preprocess_util/sourcevideo_extra.py --data_root=data/lip_src/ \
                                                          --output=output/lip_src \
                                                          --face_detect=ultra_light_fast_generic_face_detector_1mb_640