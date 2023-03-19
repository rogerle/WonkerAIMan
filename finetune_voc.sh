#!/bin/bash

set -e
source path.sh
GPU_NUM=1
gpus=1
CUDA_VISIBLE_DEVICES=${gpus}
stage=0
stop_stage=100

#微调需要训练的语音的文件
VOICE_NAME=SSB0590
VOICE_INPUT_DIR=output/${VOICE_NAME} #这里要调整把需要训练的音频文件名设置成输出目录，两者要同名
NEW_DIR_NAME='newdir'
NEW_DIR=${VOICE_INPUT_DIR}/${NEW_DIR_NAME}
MFA_DIR=output/mfa_result
DURATIONS_FILE=output/durations.txt
DUMP_DIR=output/dump
FINETUNE_OUT=exp/output
FINETUNE_CONFIG=conf/finetune.yaml
CKPT=snapshot_iter_97447
REPLACE_SPKID=65 # csmsc: 0, ljspeech: 175, aishell3: 0~173, vctk: 176
# AM参数可以设置成
# fastspeech2_csmsc,speedyspeech_csmsc,speedyspeech_aishell3,fastspeech2_ljspeech,fastspeech2_aishell3,fastspeech2_vctk'
# tacotron2_csmsc,tacotron2_ljspeech,fastspeech2_mix,fastspeech2_canton,fastspeech2_male-zh,fastspeech2_male-en,fastspeech2_male-mix
PRE_AM_TRAIN_MODEL="fastspeech2_aishell3"
# VOC参数可以设置成 'pwgan_csmsc','pwgan_ljspeech','pwgan_aishell3', 'pwgan_vctk','mb_melgan_csmsc', 'style_melgan_csmsc',
# 'hifigan_csmsc','hifigan_ljspeech','hifigan_aishell3','hifigan_vctk','wavernn_csmsc','pwgan_male','hifigan_male',
PRE_VOC_TRAIN_MODEL="hifigan_aishell3"
PRE_MODEL_DIR=data/pretrain_models
PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}
PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}

LANG='zh'

#define am_model parameters
if [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_aishell3" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_aishell3_ckpt_1.1.0
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/hifigan_aishell3_ckpt_0.2.0
elif  [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_csmsc" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_nosil_baker_ckpt_0.4
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/hifigan_csmsc_ckpt_0.1.1
elif  [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_mix" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_mix_ckpt_1.2.0
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/hifigan_aishell3_ckpt_0.2.0

elif  [ ${PRE_AM_TRAIN_MODEL} == "fastspeech2_male-mix" ];
then
  PRE_AM_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_male_mix_ckpt_1.4.0
  PRE_VOC_MODEL_DIR=${PRE_MODEL_DIR}/pwg_male_ckpt_1.4.0

fi

source ${BIN_DIR}/parse_options.sh || exit 1

if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    python ${UTILS_DIR}/finetune_gen_gta_mel.py \
        --fastspeech2-config=${PRE_AM_MODEL_DIR}/default.yaml \
        --fastspeech2-checkpoint=${PRE_AM_MODEL_DIR}/snapshot_iter_96400.pdz \
        --fastspeech2-stat=${PRE_AM_MODEL_DIR}/speech_stats.npy \
        --dur-file=${DURATIONS_FILE} \
        --output-dir=${FINETUNE_OUT}/dump_finetune \
        --phones-dict=${PRE_AM_MODEL_DIR}/phone_id_map.txt \
        --speaker-dict=${PRE_AM_MODEL_DIR}/speaker_id_map.txt \
        --speaker-id=${REPLACE_SPKID} \
        --dataset=aishell3 \
        --rootdir=~/datasets/data_aishell3/
fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    python ${UTILS_DIR}/link_wav.py \
        --old-dump-dir=${DUMP_DIR} \
        --dump-dir=${FINETUNE_OUT}/dump_finetune
fi