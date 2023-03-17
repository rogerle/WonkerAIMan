#!/bin/bash

set -e
source path.sh


PRE_AM_TRAIN_MODEL="fs2_cmscm" #参数可以设置成（fs2_aishell3,fs2_cmscm,fs2_mix,fs2_vctk）

if [ ${PRE_AM_TRAIN_MODEL} == "fs2_aishell3" ];
then
  PRE_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_aishell3_ckpt_1.1.0

  if [ ! -d ${PRE_MODEL_DIR} ];
  then
    wget -P ${PRE_MODEL_DIR} https://paddlespeech.bj.bcebos.com/Parakeet/released_models/fastspeech2/fastspeech2_aishell3_ckpt_1.1.0.zip
    unzip -d ${PRE_MODEL_DIR} ${PRE_MODEL_DIR}/fastspeech2_aishell3_ckpt_1.1.0.zip

  fi

elif  [ ${PRE_AM_TRAIN_MODEL} == "fs2_cmscm" ];
then
  PRE_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_nosil_baker_ckpt_0.4

  if [ ! -d ${PRE_MODEL_DIR} ];
  then
    wget -P ${PRE_MODEL_DIR} https://paddlespeech.bj.bcebos.com/Parakeet/released_models/fastspeech2/fastspeech2_nosil_baker_ckpt_0.4.zip
    unzip -d ${PRE_MODEL_DIR} ${PRE_MODEL_DIR}/fastspeech2_nosil_baker_ckpt_0.4.zip

  fi

elif  [ ${PRE_AM_TRAIN_MODEL} == "fs2_mix" ];
then
  PRE_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_mix_ckpt_1.2.0

  if [ ! -d ${PRE_MODEL_DIR} ];
  then
    wget -P ${PRE_MODEL_DIR} https://paddlespeech.bj.bcebos.com/Parakeet/released_models/fastspeech2/fastspeech2_mix_ckpt_1.2.0.zip
    unzip -d ${PRE_MODEL_DIR} ${PRE_MODEL_DIR}/fastspeech2_mix_ckpt_1.2.0

  fi
fi