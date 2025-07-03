# runtime/config.py

import os
import json

DEFAULT_CONFIG = {
    "node_id": os.getenv("NODE_ID", "agent-001"),
    "agent_type": os.getenv("AGENT_TYPE", "FIN"),  # FIN | LTN | NAP
    "model_path": os.getenv("MODEL_PATH", "mistral-7b-instruct"),
    "lora_dir": os.getenv("LORA_DIR", "./lora_patches"),
    "listen_port": int(os.getenv("PORT", 8080)),
    "task_limit": 100,
    "log_level": os.getenv("LOG_LEVEL", "INFO"),
    "memory_path": os.getenv("MEMORY_PATH", "./memory_cache.json")
}

def load_config_from_file(filepath: str) -> dict:
    if not os.path.exists(filepath):
        print(f"[Config] Config file not found: {filepath}, using default config.")
        return DEFAULT_CONFIG
    with open(filepath, "r") as f:
        file_config = json.load(f)
    merged_config = DEFAULT_CONFIG.copy()
    merged_config.update(file_config)
    return merged_config


def get_config() -> dict:
    return DEFAULT_CONFIG
