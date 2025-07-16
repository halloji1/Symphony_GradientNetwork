#!/bin/bash
# 定义基础路径和名称
BASE_DIR="./checkpoints"
BASE_NAME="math_gpt2_medium"  # 基础名称，后续会添加递增数字

# 查找所有以 "$BASE_NAME_" 开头的现有目录，提取数字部分
# 例如 "math_gpt2_medium_3" 会提取出 "3"
# existing_indices=$(ls -d "$BASE_DIR/$BASE_NAME"_* 2>/dev/null | \
#     sed "s/^$BASE_DIR\/$BASE_NAME_//" | \
#     grep -E '^[0-9]+$')
# # 找到最大的索引（如果没有现有目录，默认最大索引为 0）
# max_index=0
# for idx in $existing_indices; do
#     if (( idx > max_index )); then
#         max_index=$idx
#     fi
# done

# # 计算新索引（最大索引 + 1）
# new_index=$((max_index + 1))

# 构造新的保存目录路径
SAVE_DIR="$BASE_DIR/$BASE_NAME"_"1"

# 打印新目录（验证用）
echo "新的保存目录：$SAVE_DIR"

# 执行训练命令，使用新的 SAVE_DIR
export CUDA_VISIBLE_DEVICES=0,1,2,3
export OMP_NUM_THREADS=4
torchrun --nproc_per_node=4 tune_gpt.py \
  --arch=gpt2-medium \
  --MATH-dataroot=./MATH/train/*/*.json \
  --epochs=80 \
  --lr=5e-5 \
  --batch-size-per-replica=1 \
  --grad-acc-steps=4 \
  --save-dir="$SAVE_DIR" \
  --log-freq=10 > ./log/log_train1.txt 2>&1

#   --load=/workspace/fyc/Symphony_GradientNetwork/math/modeling/checkpoints/math_gpt2_medium/07-15-2025__17:15:36/final_checkpoint \