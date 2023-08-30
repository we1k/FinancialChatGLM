#!/bin/bash
CUDA_VISIBLE_DEVICES=2,3 python ./src/train_bash.py \
    --stage sft \
    --model_name_or_path ./tcdata/chatglm2-6b-hug \
    --do_predict \
    --dataset SMP \
    --dataset_dir ./data \
    --output_dir output \
    --overwrite_cache \
    --max_source_length 512 \
    --max_target_length 256 \
    --overwrite_cache true \
    --per_device_eval_batch_size 16 \
    --predict_with_generate \
    --remove_unused_columns false