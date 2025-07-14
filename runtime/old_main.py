# runtime/main.py
import sys
import os

# 获取项目根目录
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# 将项目根目录添加到 Python 搜索路径
sys.path.append(project_root)

import argparse
import logging
from runtime.config import load_config
from core.identity import IdentityManager
from core.capability import CapabilityManager
from core.memory import MemoryManager
from core.reputation import ReputationManager
from models.base_loader import load_base_model
from models.lora_manager import LoRAAgent
from tools.base import ToolBase
from tools.tool_math import MathTool
from tools.tool_translate import TranslateTool
from tools.tool_search import SearchTool

# 简化的 Agent 初始化流程（支持 TaskRequester | ComputeProvider）
def main():
    parser = argparse.ArgumentParser(description="Run Symphony Agent")
    parser.add_argument("--config", type=str, required=True, help="path to config.yaml")
    args = parser.parse_args()

    # 加载配置
    cfg = load_config(args.config)
    role = cfg.get("role", "TaskRequester")
    node_id = cfg.get("node_id", "agent-001")

    # 初始化模块
    logging.basicConfig(level=logging.INFO)
    logging.info(f"[Init] Starting agent {node_id} as {role}")

    identity = IdentityManager(node_id)
    memory = MemoryManager()
    reputation = ReputationManager()

    tools: list[ToolBase] = [MathTool(), TranslateTool(), SearchTool()]
    capabilities = CapabilityManager([t.name() for t in tools])

    # 加载模型
    model = load_base_model(cfg.get("base_model", "tinymodel"))
    lora_agent = LoRAAgent(model=model, save_dir="checkpoints")

    # 注册能力
    logging.info(f"[Capabilities] {capabilities.list_capabilities()}")

    # 启动 ISEP 探索循环（简化）
    logging.info("[Beacon] Ready to broadcast / listen")
    logging.info("[Main] Placeholder for ISEP protocol loop... (to be implemented)")

if __name__ == "__main__":
    main()
