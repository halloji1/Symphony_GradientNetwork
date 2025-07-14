import json
import argparse
from modeling.tune_gpt import run_training, get_dataset

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到 Python 搜索路径
sys.path.append(project_root)

def main():
    # 解析命令行参数，允许覆盖配置文件中的设置
    parser = argparse.ArgumentParser(description="Train math model")
    parser.add_argument('--config', default='configs/config.json', type=str, help='Path to config file')
    args = parser.parse_args()

    # 加载配置文件
    with open(args.config, 'r') as f:
        config = json.load(f)

    # 将配置合并到命令行参数中
    for key, value in config.items():
        setattr(args, key, value)

    # 获取数据集
    train_data = get_dataset(args)

    # 启动训练
    run_training(args, train_data)

if __name__ == "__main__":
    main()