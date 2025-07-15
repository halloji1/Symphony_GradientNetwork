import sys
import os
import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer
import argparse
from pathlib import Path
from datasets import load_dataset

project_root = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(project_root)
project_root = os.path.join(project_root, 'math')
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "math" / "modeling"))
sys.path.append(project_root)
print(f"Project root: {project_root}")

parser = argparse.ArgumentParser(description="使用GSM8K数据集测试数学问题推理")
parser.add_argument('--model', default='gpt2', type=str, help='模型名称')
parser.add_argument('--question', type=str, help='手动输入的数学问题')
parser.add_argument('--gsm8k_id', type=int, default=None, help='GSM8K数据集中的问题ID (0-7499)')
parser.add_argument('--random', action='store_true', help='从GSM8K随机选择问题')
args = parser.parse_args()

# 加载模型和分词器
model = GPT2LMHeadModel.from_pretrained(args.model)
tokenizer = GPT2Tokenizer.from_pretrained(args.model)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# 设置pad_token和eos_token
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token
model.config.pad_token_id = model.config.eos_token_id
model.config.eos_token_id = tokenizer.eos_token_id  # 明确 eos token


def solve_math_problem(problem):
    # 优化提示词：明确步骤数量（3步），移除冗余格式
    example = """
Example:
Problem: A store sold 1/3 of 60 items in the morning, 1/4 in the afternoon. How many sold in the evening?
Step 1: Morning sales = 60 × 1/3 = 20
Step 2: Afternoon sales = 60 × 1/4 = 15
Step 3: Evening sales = 60 - 20 - 15 = 25
Final Answer: 25
"""
    
    # 明确要求用3步解决，且生成后停止
    prompt = f"""
{example}

Problem: {problem}
Step 1: 
Step 2: 
Step 3: 
Final Answer: 
"""
    
    input_ids = tokenizer.encode(prompt, return_tensors='pt').to(device)
    
    # 优化生成参数：限制步骤，提前停止
    output_ids = model.generate(
        input_ids,
        max_new_tokens=64,  # 减少生成长度（3步足够）
        temperature=0.1,  # 降低随机性，更专注于逻辑
        early_stopping=True,  # 生成eos_token后停止
        pad_token_id=tokenizer.pad_token_id,
        eos_token_id=tokenizer.eos_token_id,
        num_return_sequences=1
    )
    
    # 解码并清理输出
    output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    # 截取到Final Answer后的内容，过滤冗余
    output = output.split("Final Answer:")[0] + "Final Answer: " + output.split("Final Answer:")[-1]
    output = output.replace("\n\n", "\n").strip()  # 去除多余空行
    
    # 提取最终答案
    final_answer_start = output.find("Final Answer:")
    if final_answer_start != -1:
        final_answer = output[final_answer_start + len("Final Answer:"):].strip()
    else:
        final_answer = "未找到答案"
    
    return output, final_answer


if __name__ == "__main__":
    # 加载GSM8K数据集
    try:
        gsm8k = load_dataset("gsm8k", "main")
        print(f"已加载GSM8K数据集，训练集大小: {len(gsm8k['train'])}")
    except Exception as e:
        print(f"无法加载GSM8K数据集: {e}")
        gsm8k = None

    # 选择问题
    if args.gsm8k_id is not None and gsm8k is not None and 0 <= args.gsm8k_id < len(gsm8k['train']):
        problem = gsm8k['train'][args.gsm8k_id]['question']
        print(f"使用GSM8K问题 (ID: {args.gsm8k_id}):\n{problem}\n")
        print(f"参考答案片段: {gsm8k['train'][args.gsm8k_id]['answer'][:100]}...\n")
    elif args.random and gsm8k is not None:
        import random
        idx = random.randint(0, len(gsm8k['train'])-1)
        problem = gsm8k['train'][idx]['question']
        print(f"随机GSM8K问题 (ID: {idx}):\n{problem}\n")
    else:
        problem = args.question or "radius=5, multiply the area by 2"
        print(f"使用问题:\n{problem}\n")

    # 生成答案
    full_solution, final_answer = solve_math_problem(problem)
    
    # 输出结果（只保留有意义的步骤）
    print("模型生成的分步解答:")
    print(full_solution)
    print(f"\n提取的答案: {final_answer}")