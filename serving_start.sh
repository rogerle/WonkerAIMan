#!/bin/bash
set -e
source path.sh
export CUDA_VISIBLE_DEVICES=0
 hub serving start -c ${UTILS_DIR}/preprocess_util/face_serving_config.json >> exp/log/face_serving.log 2>&1 &
