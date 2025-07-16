CUDA_VISIBLE_DEVICES=1 python3 -u eval_math_gpt.py \
    --arch=gpt2-medium \
    --math-dataroot=./MATH/test/*/*.json \
    --load=./checkpoints/math_gpt2_medium_final/07-15-2025__17:15:36/final_checkpoint > ./log/log_eval.txt 2>&1

#--load=/data/sauravkadavath/maths-beta__modeling__checkpoints/MATH__bbox_only_3_epochs__finetune_6_epochs__pretraining_khan_latex_loss_only__gpt117/checkpoint.pth
