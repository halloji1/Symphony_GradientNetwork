# runtime/config.py

import os
import json
import yaml

DEFAULT_CONFIG = {
    # 基础配置
    "debug": False,
    "role": "task_requester",
    "node_id": "default-agent",

    # 模型加载配置
    "base_model": "default_model",
    "load_quantized": False,
    "use_lora": False,

    # 能力注册（自动与工具匹配）
    "capabilities": [],

    # 网络参数
    "p2p": {
        "port": 7788,
        "enable_dht": False,
        "beacon_ttl": 2,
        "heartbeat_interval": 15
    },

    # LoRA 存储
    "lora": {
        "save_dir": "checkpoints/",
        "patch_interval": 300
    },

    # 日志
    "log_level": "INFO",

    # 网络适配器配置
    "network": {
        "host": "213.192.2.94",
        "port": 8000
    }
}

def load_config_from_file(filepath: str) -> dict:
    if not os.path.exists(filepath):
        print(f"[Config] Config file not found: {filepath}, using default config.")
        return DEFAULT_CONFIG
    try:
        with open(filepath, "r") as f:
            file_config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[Config] Error loading YAML file: {e}, using default config.")
        return DEFAULT_CONFIG
    merged_config = DEFAULT_CONFIG.copy()
    merged_config.update(file_config)
    return merged_config


def get_config() -> dict:
    return DEFAULT_CONFIG
