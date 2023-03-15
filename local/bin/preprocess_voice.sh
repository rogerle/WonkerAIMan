#!/bin/bash
##这个脚本用来预处理声音，对于
set -e
source path.sh
export UTIL_DIR=${MAIN_ROOT}/local/utils
export models_path=${MAIN_ROOT}/data/pretrain_models
gpus=0
am_fs2_male_mix=${models_path}/fastspeech2_male_mix_ckpt_1.4.0
voc_hifigan_male=${models_path}/hifigan_male_ckpt_1.4.0
source_path=${MAIN_ROOT}/data/source

##传入用哪个模型 am_model指am的预训练模型，voc_models指voccoder的预训练模型
am_model=$1
voc_models=$2

if [ ${am_model} == "fs2_male_mix" ];
then
  if [ -d ${am_fs2_male_mix} ];
  then
    am_ckp=${am_fs2_male_mix}/snapshot_iter_177000.pdz
    am_conf=${am_fs2_male_mix}/default.yaml
    am_speech_stats=${am_fs2_male_mix}/speech_stats.npy
  else
     echo "模型不存在，下载模型"${fs2_male_mix};
     wget -P ${models_path} https://paddlespeech.bj.bcebos.com/Parakeet/released_models/fastspeech2/fastspeech2_male_mix_ckpt_1.4.0.zip
     unzip -x -d ${models_path} ${am_fs2_male_mix}.zip
  fi
fi
if [ ${voc_models} == "hifigan_male" ];
then
  if [ -d ${voc_hifigan_male} ];
  then
    voc_ckp=${voc_hifigan_male}/snapshot_iter_630000.pdz
    voc_conf=${voc_hifigan_male}/default.yaml
    voc_spk_id=${voc_hifigan_male}/speaker_id_map.txt
  else
     echo "模型不存在，下载模型"${voc_hifigan_male};
     wget -P ${models_path} https://paddlespeech.bj.bcebos.com/Parakeet/released_models/hifigan/hifigan_male_ckpt_1.4.0.zip
     unzip -x -d ${models_path} ${voc_hifigan_male}.zip
  fi
fi


#执行音频文件处理
  python ${UTIL_DIR}/parse_audio.py \
            --input_dir=data/source \
            --output_dir=output \
            --labels_txt=labels.txt