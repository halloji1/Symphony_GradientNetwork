from models.base_loader import BaseModel
from protocol.beacon import Beacon
from protocol.response import BeaconResponse
from models.lora_manager import LoRAAdapter
from core.capability import CapabilityManager
from core.memory import LocalMemory
from protocol.lora_patch import LoRAPatch
from infra.sparta_communicator import SpartacusCommunicator
from typing import Dict
from infra.ISEP import ISEPClient
from infra.network_adapter import NetworkAdapter

class ComputeProvider:
    def __init__(self, config):
        self.id = config["node_id"]
        self.base_model = BaseModel(config["base_model"], config["sys_prompt"])
        self.lora = LoRAAdapter(self.base_model)
        self.capabilities = config["capabilities"]
        self.memory = LocalMemory()
        self.network = NetworkAdapter(self.id, config)
        self.ise = ISEPClient(self.id, self.network)

        # self.sparta_communicator = SpartacusCommunicator(id, self.config)
        # self.sparta_communicator.register_callback(self._handle_received_patch)
        # self.sparta_communicator.start()

        self.received_patches = []

    def handle_beacon(self, sender_id: str, beacon: Beacon):
        # 计算能力得分
        score = self.capab_manager.match(beacon.requirement)
        # 创建 BeaconResponse
        response = BeaconResponse(self.id, self.capab_manager.capabilities, match_score=score)
        # 发送响应
        self.ise.send_response(sender_id, "beacon_response", response)

    def execute(self, subtask):
        """
        调用本地模型完成子任务
        """
        try:
            # 提取任务描述
            task_description = subtask.get("desc")
            if not task_description:
                raise ValueError("Task description is missing in task data.")

            # 调用本地模型生成结果
            result = self.base_model.generate(task_description)

            # 存储结果到本地内存
            self.memory.store_result({"task": subtask, "result": result})

            return result
        except Exception as e:
            print(f"[ComputeProvider] Error executing task: {str(e)}")
            return None
    
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

        # self.sparta_communicator.broadcast_lora_patch(patch)
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