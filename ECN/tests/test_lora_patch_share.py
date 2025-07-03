# tests/test_lora_patch_share.py

from protocol.lora_patch import LoRAPatch
import torch
import os

# 模拟生成一个简单 patch
source_id = "node-A"
fake_state_dict = {"adapter.layer.1": torch.tensor([1.0, 2.0]), "adapter.layer.2": torch.tensor([3.0])}
patch = LoRAPatch(source_id=source_id, patch_path="", layer_names=list(fake_state_dict.keys()))
saved_path = patch.save_patch(fake_state_dict)
print("[Patch Saved]", saved_path)

# 模拟另一个节点加载 patch
try:
    loaded = patch.load_patch()
    print("[Patch Loaded] Keys:", list(loaded.keys()))
except Exception as e:
    print("[Patch Error]", e)
