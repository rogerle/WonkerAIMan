#!/bin/bash

set -e
source path.sh
model_path=${MAIN_ROOT}/data/pretrain_models
source_path=${MAIN_ROOT}/data/source
run_param=${1}
# with the following command, you can choose the stage range you want to run
# such as `./run.sh --stage 0 --stop-stage 0`
# this can not be mixed use with `$1`, `$2` ...
if [ ${run_param} = "all" ] || [ ${run_param} = "voice" ] ;
then
    source ${BIN_DIR}/preprocess_voice.sh || exit -1
fi

