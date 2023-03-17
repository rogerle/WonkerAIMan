#!/bin/bash

set -e
source path.sh

echo 'start asr server'
python ${UTILS_DIR}/asr_server.py \
                        --config_file=${CONF_DIR}/asr/ws_conformer_wenetspeech_application.yaml
                        --log_file=exp/wonker_asr.log
echo 'server started'