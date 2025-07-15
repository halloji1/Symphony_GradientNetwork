CUDA_VISIBLE_DEVICES=1 python3 -u eval_math_gpt.py \
    --arch=gpt2 \
    --math-dataroot=./MATH/test/*/*.json \
    --load=./checkpoints/math_gpt2_final/07-15-2025__16:30:22/final_checkpoint > ./log/log_eval.txt 2>&1

#--load=/data/sauravkadavath/maths-beta__modeling__checkpoints/MATH__bbox_only_3_epochs__finetune_6_epochs__pretraining_khan_latex_loss_only__gpt117/checkpoint.pth
