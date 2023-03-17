#!/bin/bash
export MAIN_ROOT=`realpath ${PWD}`
export PATH=${MAIN_ROOT}:${MAIN_ROOT}/local:${MAIN_ROOT}/local/utils:${PATH}
export LC_ALL=C

export PYTHONDONTWRITEBYTECODE=1
# Use UTF-8 in Python to avoid UnicodeDecodeError when LC_ALL=C
export PYTHONIOENCODING=UTF-8
export PYTHONPATH=${MAIN_ROOT}:${PYTHONPATH}

export BIN_DIR=${MAIN_ROOT}/local/bin
export UTILS_DIR=${MAIN_ROOT}/local/utils
export TOOLS_DIR=${MAIN_ROOT}/local/tools
export CONF_DIR=${MAIN_ROOT}/conf
export LOG_DIR=${MAIN_ROOT}/exp/log

