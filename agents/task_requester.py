from models.base_loader import BaseModel
from models.lora_manager import LoRAAdapter
from protocol.beacon import Beacon, BeaconResponse
from core.capability import match_capability
from core.reputation import update_reputation
from core.memory import LocalMemory
from protocol.task_contract import TaskDAG, SubTask
from p2p.network import ISEPClient

class TaskRequester:
    def __init__(self, id, model_path, sys_prompt, capabilities):
        self.id = id
        self.base_model = BaseModel(model_path, sys_prompt)
        self.lora = LoRAAdapter(self.base_model)
        self.capabilities = capabilities
        self.memory = LocalMemory()
        self.ise = ISEPClient(self.id)

    def handle_beacon(self, beacon: Beacon):
        if match_capability(beacon.requirement, self.capabilities):
            return BeaconResponse(self.id, self.capabilities)
        return None

    def decompose_task(self, task_description: str) -> TaskDAG:
        dag_structure = self.base_model.generate_task_dag(task_description)
        return TaskDAG.from_structure(dag_structure)

    def assign_subtasks(self, task_dag: TaskDAG):
        for subtask in task_dag.subtasks:
            beacon = Beacon(
                sender=self.id,
                task_id=subtask.id,
                requirement=subtask.requirement,
                ttl=2
            )
            candidates = self.ise.broadcast_and_collect(beacon)
            best_match = self.select_executor(candidates, subtask)
            if best_match:
                self.ise.delegate_task(best_match, subtask)

    def select_executor(self, candidates, subtask):
        # Placeholder for scoring logic
        return candidates[0] if candidates else None

    def evaluate_and_update(self, task_result, reward_score):
        self.lora.update_from_reward(reward_score)
        update_reputation(task_result.source_id, reward_score)
        self.memory.store_result(task_result)