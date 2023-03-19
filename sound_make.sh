#!/bin/bash

set -e
source path.sh
GPU_NUM=1
gpus=1
CUDA_VISIBLE_DEVICES=${gpus}
REPLACE_SPKID=21
# AM参数可以设置成
# fastspeech2_csmsc,speedyspeech_csmsc,speedyspeech_aishell3,fastspeech2_ljspeech,fastspeech2_aishell3,fastspeech2_vctk'
# tacotron2_csmsc,tacotron2_ljspeech,fastspeech2_mix,fastspeech2_canton,fastspeech2_male-zh,fastspeech2_male-en,fastspeech2_male-mix
PRE_AM_TRAIN_MODEL="fastspeech2_mix"
# VOC参数可以设置成 'pwgan_csmsc','pwgan_ljspeech','pwgan_aishell3', 'pwgan_vctk','mb_melgan_csmsc', 'style_melgan_csmsc',
# 'hifigan_csmsc','hifigan_ljspeech','hifigan_aishell3','hifigan_vctk','wavernn_csmsc','pwgan_male','hifigan_male',
PRE_VOC_TRAIN_MODEL="hifigan_aishell3"
PRE_MODEL_DIR=data/pretrain_models
PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}
PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}
OUTPUT_DIR=exp/output

LANG='zh'

#define am_model parameters
if [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_aishell3" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_aishell3_ckpt_1.1.0
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/hifigan_aishell3_ckpt_0.2.0
  SNAP_SHOT=snapshot_iter_96400

elif  [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_csmsc" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_nosil_baker_ckpt_0.4
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/hifigan_csmsc_ckpt_0.1.1
  SNAP_SHOT=snapshot_iter_76000

elif  [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_mix" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_mix_ckpt_1.2.0
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/hifigan_aishell3_ckpt_0.2.0
  SNAP_SHOT=snapshot_iter_2500000

elif  [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_male" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_male_mix_ckpt_1.4.0
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/pwg_male_ckpt_1.4.0
  SNAP_SHOT=snapshot_iter_200000

fi

python ${UTILS_DIR}/tts_local.py \
        --output=${OUTPUT_DIR} \
        --am=${PRE_AM_TRAIN_MODEL} \
        --am_config=${PRE_AM_MODEL_DIR}/default.yaml \
        --am_ckpt=${PRE_AM_MODEL_DIR}/snapshot_iter_99200.pdz \
        --am_stat=${PRE_AM_MODEL_DIR}/speech_stats.npy \
        --spk_id=${REPLACE_SPKID} \
        --phones_dict=${PRE_AM_MODEL_DIR}/phone_id_map.txt \
        --speaker_dict=${PRE_AM_MODEL_DIR}/speaker_id_map.txt \
        --voc=${PRE_VOC_TRAIN_MODEL} \
        --voc_config=${PRE_VOC_MODEL_DIR}/default.yaml \
        --voc_ckpt=${PRE_VOC_MODEL_DIR}/${SNAP_SHOT}.pdz \
        --voc_stat=${PRE_VOC_MODEL_DIR}/feats_stats.npy \
        --lang=mix \
        --ngpu=${GPU_NUM} \
        --sentences_txt=data/source/sentences_mix.txt
