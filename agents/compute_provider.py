from models.base_loader import BaseModel
from protocol.beacon import Beacon
from models.lora_manager import LoRAAdapter
from core.capability import match_capability
from tools.base_tool import load_tool
from core.memory import LocalMemory
from protocol.lora_patch import LoRAPatch
from infra.sparta_communicator import SpartacusCommunicator
from typing import Dict

class ComputeProvider:
    def __init__(self, id, model_path, sys_prompt, tools):
        self.id = id
        self.base_model = BaseModel(model_path, sys_prompt)
        self.lora = LoRAAdapter(self.base_model)
        self.capabilities = tools
        self.tool_modules = {tool: load_tool(tool) for tool in tools}
        self.memory = LocalMemory()

        self.sparta_communicator = SpartacusCommunicator(id, self.config)
        self.sparta_communicator.register_callback(self._handle_received_patch)
        self.sparta_communicator.start()

        self.received_patches = []

    def handle_beacon(self, beacon: Beacon):
        if match_capability(beacon.requirement, self.capabilities):
            return True
        return False

    def execute(self, task_data):
        tool_name = task_data.get("tool")
        tool = self.tool_modules.get(tool_name)
        if not tool:
            raise Exception(f"Tool '{tool_name}' not available.")
        result = tool.execute(task_data)
        self.memory.store_result(result)
        return result
    
    def evaluate_and_update(self, task_result, reward_score):
        prev_state = self.lora.model.state_dict()
        self.lora.update_from_reward(reward_score)
        self.memory.store_result(task_result)

        sparse_delta = self.lora.get_sparse_delta(prev_state)
        patch = LoRAPatch(
            source_id=self.id,
            patch_path="",
            layer_names=list(sparse_delta.keys()),
            is_sparse=True
        )
        saved_path = patch.save_patch(sparse_delta)

        self.sparta_communicator.broadcast_lora_patch(patch)
        return patch
    
    def _handle_received_patch(self, patch: LoRAPatch):
        self.received_patches.append(patch)

        self.apply_received_patch(patch)
        
    def apply_received_patch(self, patch: LoRAPatch):
        try:
            patch_data = patch.load_patch()

            self.lora.apply_patch(patch_data)
            
        except Exception as e:
            print(f"[ComputeProvider] 应用LoRA patch时出错: {str(e)}")