#!/bin/bash

set -e
source path.sh
source_path=${MAIN_ROOT}/data/source
run_param=${1}

if [ ${run_param} = "all" ] || [ ${run_param} = "preprocess_voc" ];
then
    ##参数前面一个代表am 后面一个代表voc,目前支持的模型am{fs2_male_mix} voc{hifigan_male}
    source ${BIN_DIR}/preprocess_voice.sh fs2_male_mix hifigan_male || exit -1;
fi

