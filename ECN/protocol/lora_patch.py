# protocol/lora_patch.py

import os
import torch
import time
import uuid
from typing import Dict

class LoRAPatch:
    def __init__(self, source_id: str, patch_path: str, layer_names: list):
        self.patch_id = str(uuid.uuid4())
        self.source_id = source_id              # 发起共享 patch 的节点 ID
        self.patch_path = patch_path            # 本地存储路径
        self.layer_names = layer_names          # 被更新的 LoRA 层名
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        return {
            "patch_id": self.patch_id,
            "source_id": self.source_id,
            "patch_path": self.patch_path,
            "layer_names": self.layer_names,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict) -> 'LoRAPatch':
        return LoRAPatch(
            source_id=data.get("source_id", "unknown"),
            patch_path=data.get("patch_path", ""),
            layer_names=data.get("layer_names", []),
        )

    def save_patch(self, state_dict, save_dir="shared_patches"):
        os.makedirs(save_dir, exist_ok=True)
        filename = f"patch_{self.source_id[:6]}_{self.patch_id[:6]}.pt"
        full_path = os.path.join(save_dir, filename)
        torch.save(state_dict, full_path)
        self.patch_path = full_path
        print(f"[LoRA Patch] Saved to {full_path}")
        return full_path

    def load_patch(self):
        if not os.path.exists(self.patch_path):
            raise FileNotFoundError(f"Patch not found: {self.patch_path}")
        return torch.load(self.patch_path)

    def __repr__(self):
        return f"<LoRAPatch {self.patch_id[:6]} from {self.source_id} | Layers: {self.layer_names}>"