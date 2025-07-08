# models/lora_manager.py

from peft import LoraModel, LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import AutoModelForCausalLM
import torch
import os
import json
from typing import Dict

class LoRAAdapter:
    def __init__(self, base_model, r=8, alpha=16, dropout=0.1, lora_dir="lora_patches", sparsity_threshold=0.01):
        self.base_model = base_model
        self.model = base_model.model
        self.tokenizer = base_model.tokenizer
        self.lora_dir = lora_dir
        self.sparcity_threshold = sparsity_threshold
        os.makedirs(self.lora_dir, exist_ok=True)

        self.config = LoraConfig(
            r=r,
            lora_alpha=alpha,
            target_modules=["q_proj", "v_proj"],
            lora_dropout=dropout,
            bias="none",
            task_type="CAUSAL_LM"
        )
        self.model = prepare_model_for_kbit_training(self.model)
        self.model = get_peft_model(self.model, self.config)
        self.optimizer = torch.optim.Adam(self.model.parameters(), lr=1e-4)

    def update_from_reward(self, reward_signal: float):
        # Placeholder: apply dummy gradient update for simulation
        loss = torch.tensor(1.0 - reward_signal, requires_grad=True)
        loss.backward()
        self.optimizer.step()
        self.optimizer.zero_grad()

    def export_patch(self, filename: str = None):
        fname = filename or f"lora_patch_{self.base_model.model_path.replace('/', '_')}.bin"
        path = os.path.join(self.lora_dir, fname)
        torch.save(self.model.state_dict(), path)
        print(f"[LoRA] Patch saved to {path}")
        return path

    def load_patch(self, patch_path: str):
        state = torch.load(patch_path)
        self.model.load_state_dict(state, strict=False)
        print(f"[LoRA] Patch loaded from {patch_path}")

    def generate_with_lora(self, input_text: str, **kwargs):
        prompt = self.base_model.system_prompt + input_text
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.base_model.device)
        outputs = self.model.generate(**inputs, **kwargs)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def get_sparse_delta(self, prev_state):
        current_state = self.model.state_dict()
        delta = {}
        for key in current_state.keys():
            if key in prev_state:
                delta[key] = current_state[key] - prev_state[key]
            else:
                delta[key] = current_state[key]

        sparse_delta = {}
        for key, value in delta.items():
            abs_val = torch.abs(value).flatten()
            k = int((self.sparcity_threshold) * abs_val.numel())

            if k == 0:
                mask = torch.zeros_like(value, dtype=torch.bool)
            else:
                threshold = torch.kthvalue(abs_val, k).values
                mask = torch.abs(value) >= threshold

            sparse_delta[key] = value * mask

        return sparse_delta
    
    def apply_patch(self, patch_data: Dict):
        current_state = self.get_lora_state()
        
        for key, delta in patch_data.items():
            if key in current_state:
                current_state[key] += delta
                
        self.set_lora_state(current_state)