# # 测试已见数据（训练集），批次大小4
# CUDA_VISIBLE_DEVICES=2 python3 eval_batch.py \
#     --arch=gpt2-large \
#     --math-dataroot=./MATH/train/*/*.json \
#     --load=/workspace/fyc/Symphony_GradientNetwork/math/modeling/checkpoints/math_gpt2_medium/07-15-2025__17:15:36/final_checkpoint \
#     --data_type=train \
#     --batch_size=4

CUDA_VISIBLE_DEVICES=1 python3 -u eval_batch.py \
    --arch=gpt2-medium \
    --math-dataroot=./MATH/train/*/*.json \
    --load=./checkpoints/math_gpt2_medium/07-15-2025__17:15:36/final_checkpoint \
    --sample=1000 > ./log/log_eval.txt 2>&1
