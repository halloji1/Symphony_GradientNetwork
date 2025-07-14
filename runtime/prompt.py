import sys
import os

# 获取项目根目录的绝对路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到系统路径
sys.path.append(project_root)

from modeling.tune_gpt import get_dataset
import argparse


def divide_and_collaborate(problem):
    # 示例：将复杂问题拆分为子问题
    sub_problems = [
        "第一步：计算问题的某个中间结果",
        "第二步：根据中间结果计算最终答案"
    ]
    intermediate_result = None
    for sub_problem in sub_problems:
        # 结合原问题和子问题
        input_problem = f"{problem} {sub_problem}"
        input_ids = tokenizer.encode(input_problem, return_tensors='pt').to(model.device)
        output_ids = model.generate(
            input_ids, 
            num_beams=5, 
            early_stopping=True,
            temperature=1.0,
            max_length=384 if args.arch == 'gpt2-xl' else 1024
        )
        output_str = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        if intermediate_result is None:
            intermediate_result = output_str
        else:
            final_answer = output_str
    return final_answer

# 示例复杂问题
complex_problem = "计算一个半径为 5 的圆的面积，然后将结果乘以 2"
answer = divide_and_collaborate(complex_problem)
print(f"复杂问题的答案: {answer}")


# 解析命令行参数
parser = argparse.ArgumentParser(description="Prepare math dataset")
parser.add_argument('--MATH_dataroot', default='./MATH/test/*/*.json', type=str, help='Path to MATH dataset')
parser.add_argument('--arch', default='gpt2', type=str, help='Model architecture')
args = parser.parse_args()

# 获取数据集
eval_data = get_dataset(args)
dataloader = torch.utils.data.DataLoader(
    eval_data, 
    batch_size=1, 
    num_workers=0, 
    pin_memory=True
)


from tqdm import tqdm

for i, batch in enumerate(tqdm(dataloader)):
    input_ids = batch['input_ids'].to(model.device)
    output_ids = model.generate(
        input_ids, 
        num_beams=5, 
        early_stopping=True,
        temperature=1.0,
        max_length=384 if args.arch == 'gpt2-xl' else 1024
    )
    output_str = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    print(f"问题: {tokenizer.decode(input_ids[0])}")
    print(f"答案: {output_str}")
    print("-" * 50)