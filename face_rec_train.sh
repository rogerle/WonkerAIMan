#!/bin/bash

set -e
source path.sh

python ${UTILS_DIR}/preprocess_util/face_recognition_train.py \
                                    --data_root=data/waves \
                                    --device=gpu \
                                    --ckpt_dir=data/face_models \
                                    --batch_size=8 \
                                    --epcho=100 \
                                    --save_interval=10 \
                                    --save_log_interval=10

rm -rf data/face_models/epoch*

hub serving start --config ${UTILS_DIR}/preprocess_util/face_serving_config.json
