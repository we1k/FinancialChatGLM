#!/bin/bash

accelerate launch ./src/train_bash.py \
    --stage sft \
    --do_train \
    --model_name_or_path THUDM/chatglm2-6b \
    --dataset SMP \
    --dataset_dir ./data \
    --finetuning_type lora \
    --output_dir checkpoint/smp \
    --overwrite_cache \
    --per_device_train_batch_size 4 \
    --gradient_accumulation_steps 4 \
    --max_source_length 256 \
    --max_target_length 256 \
    --lr_scheduler_type cosine \
    --logging_steps 10 \
    --save_steps 1000 \
    --learning_rate 5e-5 \
    --num_train_epochs 1.0 \
    --fp16