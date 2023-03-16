#!/bin/bash

set -e
source path.sh
GPU_NUM=1
gpus=1
CUDA_VISIBLE_DEVICES=${gpus}
stage=0
stop_stage=100

#微调需要训练的语音的文件
VOICE_INPUT_DIR=output/LJ_Voice
NEW_DIR_NAME='newdir'
NEW_DIR=${VOICE_INPUT_DIR}/${NEW_DIR_NAME}
MFA_DIR=output/mfa_result
DURATIONS_FILE=output/durations.txt
DUMP_DIR=output/dump
FINETUNE_OUT=exp/output
FINETUNE_CONFIG=conf/finetune.yaml
REPLACE_SPKID=21 # csmsc: 174, ljspeech: 175, aishell3: 0~173, vctk: 176

PRE_AM_TRAIN_MODEL="fs2_aishell3" #参数可以设置成（fs2_aishell3,fs2_cmscm,fs2_mix,fs2_vctk）
PRE_VOC_TRAIN_MODEL="hifigan_aishell3" #参数可以设置成（hifigan_aishell3,hifigan_vctk）
PRE_MODEL_DIR=data/pretrain_models

LANG='zh'

#define model parameters
if [ ${PRE_AM_TRAIN_MODEL} == "fs2_aishell3" ] || [${PRE_AM_TRAIN_MODEL} == "fs2_cmscm" ];
then
  PRE_MODEL_DIR=${PRE_MODEL_DIR}/fastspeech2_aishell3_ckpt_1.1.0
fi

# with the following command, you can choose the stage range you want to run
# such as `./run.sh --stage 0 --stop-stage 0`
# this can not be mixed use with `$1`, `$2` ...
source ${BIN_DIR}/parse_options.sh || exit 1

# check oov
if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    echo "###################################"
    echo "#   STEP 1.分割音频并生成标记文件     #"
    echo "###################################"
    ${BIN_DIR}/parse_sourceaudio.sh || exit -1;
fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    echo "###################################"
    echo "# STEP 2.检查labels里面是否有异   #"
    echo "#   常发音                        #"
    echo "###################################"
    echo "检查预制文件"
    python3 ${UTILS_DIR}/check_oov.py \
        --input_dir=${VOICE_INPUT_DIR} \
        --pretrained_model_dir=${PRE_MODEL_DIR} \
        --newdir_name=${NEW_DIR_NAME} \
        --lang=${LANG}
    echo "检查结束"
fi

##开始mfa对齐操作
if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    echo "###################################"
    echo "#### STEP 2.开始mfa对齐操作 #######"
    echo "###################################"
    python3 ${UTILS_DIR}/get_mfa_result.py \
        --input_dir=${NEW_DIR} \
        --mfa_dir=${MFA_DIR} \
        --lang=${LANG}
fi

##生成durations.txt
if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    echo "###################################"
    echo "#### STEP 3.生成durations.txt #######"
    echo "###################################"
    python3 ${UTILS_DIR}/generate_duration.py \
        --mfa_dir=${MFA_DIR} \
        --durations_file=${DURATIONS_FILE}
fi

##展开特征文件
if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    echo "###################################"
    echo "#### STEP 4.展开特征文件 #######"
    echo "###################################"
    python3 ${UTILS_DIR}/extract_feature.py \
        --duration_file=${DURATIONS_FILE} \
        --input_dir=${NEW_DIR} \
        --dump_dir=${DUMP_DIR} \
        --pretrained_model_dir=${PRE_MODEL_DIR} \
        --replace_spkid=${REPLACE_SPKID}
fi

# create finetune env
if [ ${stage} -le 5 ] && [ ${stop_stage} -ge 5 ]; then
    echo "###################################"
    echo "#### STEP 5.准备finetune的环境 #######"
    echo "###################################"
    echo "create finetune env"
    python3 ${UTILS_DIR}/prepare_env.py \
        --pretrained_model_dir=${PRE_MODEL_DIR} \
        --output_dir=${FINETUNE_OUT}
fi

# finetune
if [ ${stage} -le 6 ] && [ ${stop_stage} -ge 6 ]; then
    echo "finetune..."
    python3 ${UTILS_DIR}/finetune.py \
        --pretrained_model_dir=${PRE_MODEL_DIR} \
        --dump_dir=${DUMP_DIR} \
        --output_dir=${FINETUNE_OUT} \
        --ngpu=${GPU_NUM} \
        --epoch=110 \
        --finetune_config=${FINETUNE_CONFIG}
fi