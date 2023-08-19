#! /bin/bash
echo "this is a test"
nvidia-smi

export CUDA_VISIBLE_DEVICES='2, 3'
export WANDB_LOG_MODEL=true
# export WANDB_MODE=disabled
gpu_num=$(echo $CUDA_VISIBLE_DEVICES | awk -F ',' '{print NF}')
echo $gpu_num $CUDA_VISIBLE_DEVICES
