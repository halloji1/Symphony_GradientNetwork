from models.base_loader import BaseModel
from protocol.beacon import Beacon
from protocol.response import BeaconResponse
from models.lora_manager import LoRAAdapter
from core.capability import CapabilityManager
from core.memory import LocalMemory
from protocol.lora_patch import LoRAPatch
from infra.sparta_communicator import SpartacusCommunicator
from protocol.task_contract import TaskContract, TaskResult, Task
from typing import Dict
from infra.ISEP import ISEPClient
from infra.network_adapter import NetworkAdapter

class User:
    def __init__(self, config, cot_num):
        self.id = config["node_id"]
        self.network = NetworkAdapter(self.id, config)
        self.ise = ISEPClient(self.id, self.network)
        self.cot_num = cot_num
        
        for neighbor in config["neighbours"]:
            self.network.add_neighbor(neighbor[0], neighbor[1], int(neighbor[2]))
        
    def assign_original_task(self, user_input):
        task = Task(subtask_id=0, steps={}, previous_results=[], original_problem=user_input, final_result="", user_id=self.id)
        beacon = Beacon(sender=self.id, task_id=str(task.subtask_id), requirement="Plan", ttl=2)
        candidates = self.ise.broadcast_and_collect(beacon)
        best_matches = self.select_executor(candidates, self.cot_num)
        for match in best_matches:
            self.ise.delegate_task(match[0], task)
    
    def select_executor(self, candidates, num):
        return candidates[:num]