#!/bin/bash
##这个脚本用来预处理声音，对于
set -e
source path.sh
export UTIL_DIR=${MAIN_ROOT}/local/utils
models_path=${MAIN_ROOT}/data/pretrain_models
gpus=0
am_fs2_malemix=${models_path}/fastspeech2_male_mix_ckpt_1.4.0
source_path=${MAIN_ROOT}/data/source

model_path=""
##传入用哪个模型 am_model指am的预训练模型，voc_models指voccoder的预训练模型
am_model=$1
voc_models=$2

if [ ${am_model} == "fs2_male_mix" ];
then
  if [ ! -d ${am_fs2_malemix} ];
    am_ckp=${am_fs2_malemix}/snapshot_iter_177000.pdz
    am_conf=${am_fs2_malemix}/default.yaml
    am_spk_id=${am_fs2_malemix}/speaker_id_map.txt
    am_speech_stats=${am_fs2_malemix}/speech_stats.npy
    python ${UTIL_DIR}/parse_audio.py \
            --input_dir=data/source \
            --output_dir=output
  then
     echo "模型不存在，请下载模型。本应用支持(fs2_male_mix)等模型"
  fi
fi