#!/bin/bash

set -e
source path.sh
GPU_NUM=1
gpus=1
CUDA_VISIBLE_DEVICES=${gpus}
stage=0
stop_stage=100

#微调需要训练的语音的文件
VOICE_NAME=SSB0784
VOICE_INPUT_DIR=output/${VOICE_NAME} #这里要调整把需要训练的音频文件名设置成输出目录，两者要同名
NEW_DIR_NAME='newdir'
NEW_DIR=${VOICE_INPUT_DIR}/${NEW_DIR_NAME}
MFA_DIR=output/mfa_result
DURATIONS_FILE=output/durations.txt
DUMP_DIR=output/dump
FINETUNE_OUT=exp/output
FINETUNE_CONFIG=conf/finetune.yaml
CKPT=snapshot_iter_106960
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

# with the following command, you can choose the stage range you want to run
# such as `./fintune_aino.sh --stage 0 --stop-stage 0`
# this can not be mixed use with `$1`, `$2` ...
source ${BIN_DIR}/parse_options.sh || exit 1

# check oov
if [ ${stage} -le 0 ] && [ ${stop_stage} -ge 0 ]; then
    echo "###################################"
    echo "#   STEP 1.分割音频并生成标记文件     #"
    echo "###################################"
    echo 'start split source wav files'
    start_asr_server.sh &> exp/log/streaming_asr.log&
    sleep 10
    ${BIN_DIR}/parse_sourceaudio.sh ${VOICE_NAME}.wav || exit -1;

fi

if [ ${stage} -le 1 ] && [ ${stop_stage} -ge 1 ]; then
    echo 'generate labels'
    python  ${UTILS_DIR}/py.py --content_txt=${VOICE_INPUT_DIR}/content.txt \
              --labels_txt=${VOICE_INPUT_DIR}/labels.txt \
              --voice_name=$VOICE_NAME
fi

if [ ${stage} -le 2 ] && [ ${stop_stage} -ge 2 ]; then
    echo "###################################"
    echo "# STEP 2.检查labels里面是否有异   #"
    echo "#   常发音                        #"
    echo "###################################"
    echo "检查预制文件"
    python ${UTILS_DIR}/check_oov.py \
        --input_dir=${VOICE_INPUT_DIR} \
        --pretrained_model_dir=${PRE_AM_MODEL_DIR} \
        --newdir_name=${NEW_DIR_NAME} \
        --lang=${LANG}
    echo "检查结束"
fi

##开始mfa对齐操作
if [ ${stage} -le 3 ] && [ ${stop_stage} -ge 3 ]; then
    echo "###################################"
    echo "#### STEP 3.开始mfa对齐操作 #######"
    echo "###################################"
    python ${UTILS_DIR}/get_mfa_result.py \
        --input_dir=${NEW_DIR} \
        --mfa_dir=${MFA_DIR} \
        --lang=${LANG}
fi

##生成durations.txt
if [ ${stage} -le 4 ] && [ ${stop_stage} -ge 4 ]; then
    echo "###################################"
    echo "#### STEP 4.生成durations.txt #######"
    echo "###################################"
    python ${UTILS_DIR}/generate_duration.py \
        --mfa_dir=${MFA_DIR} \
        --durations_file=${DURATIONS_FILE}

    echo 'durations.txt done!'
fi

##展开特征文件
if [ ${stage} -le 5 ] && [ ${stop_stage} -ge 5 ]; then
    echo "###################################"
    echo "#### STEP 5.展开特征文件 #######"
    echo "###################################"
    python ${UTILS_DIR}/extract_feature.py \
        --duration_file=${DURATIONS_FILE} \
        --input_dir=${NEW_DIR} \
        --dump_dir=${DUMP_DIR} \
        --pretrained_model_dir=${PRE_AM_MODEL_DIR} \
        --replace_spkid=${REPLACE_SPKID}
fi

if [ ${stage} -le 6 ] && [ ${stop_stage} -ge 6 ]; then
    echo "###################################"
    echo "#### STEP 6.计算npy文件 #######"
    echo "###################################"
    python ${UTILS_DIR}/compute_statistics.py \
        --metadata=${DUMP_DIR}/train/raw/metadata.jsonl \
        --field-name="speech"

    python ${UTILS_DIR}/compute_statistics.py \
        --metadata=${DUMP_DIR}/train/raw/metadata.jsonl \
        --field-name="pitch"

    python ${UTILS_DIR}/compute_statistics.py \
        --metadata=${DUMP_DIR}/train/raw/metadata.jsonl \
        --field-name="energy"


    echo "Normalize ..."
    python ${UTILS_DIR}/norms_fs2.py \
        --metadata=${DUMP_DIR}/train/raw/metadata.jsonl \
        --dumpdir=${DUMP_DIR}/train/norm \
        --speech-stats=${DUMP_DIR}/train/speech_stats.npy \
        --pitch-stats=${DUMP_DIR}/train/pitch_stats.npy \
        --energy-stats=${DUMP_DIR}/train/energy_stats.npy \
        --phones-dict=${DUMP_DIR}/phone_id_map.txt \
        --speaker-dict=${DUMP_DIR}/speaker_id_map.txt

    python ${UTILS_DIR}/norms_fs2.py \
        --metadata=${DUMP_DIR}/dev/raw/metadata.jsonl \
        --dumpdir=${DUMP_DIR}/dev/norm \
        --speech-stats=${DUMP_DIR}/train/speech_stats.npy \
        --pitch-stats=${DUMP_DIR}/train/pitch_stats.npy \
        --energy-stats=${DUMP_DIR}/train/energy_stats.npy \
        --phones-dict=${DUMP_DIR}/phone_id_map.txt \
        --speaker-dict=${DUMP_DIR}/speaker_id_map.txt

    python ${UTILS_DIR}/norms_fs2.py \
        --metadata=${DUMP_DIR}/test/raw/metadata.jsonl \
        --dumpdir=${DUMP_DIR}/test/norm \
        --speech-stats=${DUMP_DIR}/train/speech_stats.npy \
        --pitch-stats=${DUMP_DIR}/train/pitch_stats.npy \
        --energy-stats=${DUMP_DIR}/train/energy_stats.npy \
        --phones-dict=${DUMP_DIR}/phone_id_map.txt \
        --speaker-dict=${DUMP_DIR}/speaker_id_map.txt
fi

# create finetune env
if [ ${stage} -le 7 ] && [ ${stop_stage} -ge 7 ]; then
    echo "###################################"
    echo "#### STEP 7.准备finetune的环境 #######"
    echo "###################################"
    echo "create finetune env"
    python ${UTILS_DIR}/prepare_env.py \
        --pretrained_model_dir=${PRE_AM_MODEL_DIR} \
        --output_dir=${FINETUNE_OUT}
fi

# finetune
if [ ${stage} -le 8 ] && [ ${stop_stage} -ge 8 ]; then
    echo "###################################"
    echo "#### STEP 8. 开始finetune的 #######"
    echo "###################################"
    echo "finetune..."
    python ${UTILS_DIR}/finetune.py \
        --pretrained_model_dir=${PRE_AM_MODEL_DIR} \
        --dump_dir=${DUMP_DIR} \
        --output_dir=${FINETUNE_OUT} \
        --ngpu=${GPU_NUM} \
        --epoch=1500 \
        --finetune_config=${FINETUNE_CONFIG}
fi

# synthesize e2e
if [ ${stage} -le 9 ] && [ ${stop_stage} -ge 9 ]; then
    echo "###################################"
    echo "#### STEP 9. 测试输出声音 #######"
    echo "###################################"
  python ${UTILS_DIR}/synthesize_e2e.py \
        --am=${PRE_AM_TRAIN_MODEL} \
        --am_config=${PRE_AM_MODEL_DIR}/default.yaml \
        --am_ckpt=${FINETUNE_OUT}/checkpoints/${CKPT}.pdz \
        --am_stat=${DUMP_DIR}/train/speech_stats.npy \
        --voc=${PRE_VOC_TRAIN_MODEL} \
        --voc_config=${PRE_VOC_MODEL_DIR}/default.yaml \
        --voc_ckpt=${PRE_VOC_MODEL_DIR}/snapshot_iter_2500000.pdz \
        --voc_stat=${PRE_VOC_MODEL_DIR}/feats_stats.npy \
        --lang=mix \
        --text=${SOURCE_DIR}/sentences_mix.txt \
        --output_dir=output/test_e2e \
        --phones_dict=${DUMP_DIR}/phone_id_map.txt \
        --speaker_dict=${DUMP_DIR}/speaker_id_map.txt \
        --spk_id=${REPLACE_SPKID}
fi

if [ ${stage} -le 10 ] && [ ${stop_stage} -ge 10 ]; then
  ps -ef | grep asr_server | awk '{print $2}' | xargs kill -9 || exit -1;

fi


