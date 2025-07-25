from models.base_loader import BaseModel
from models.lora_manager import LoRAAdapter
from protocol.beacon import Beacon
from protocol.response import BeaconResponse
from core.capability import CapabilityManager
from core.memory import LocalMemory
from protocol.task_contract import TaskDAG, SubTask, TaskAllocation
from infra.ISEP import ISEPClient
from infra.network_adapter import NetworkAdapter
import random
import json

class TaskRequester:
    def __init__(self, config):
        self.id = config["node_id"]
        self.gpu_id = config.get("gpu_id", 0)
        if config["base_model"] == "test":
            self.base_model = None
        else:
            self.base_model = BaseModel(config["base_model"], config["sys_prompt"], device=f"cuda:{self.gpu_id}")
            self.lora = LoRAAdapter(self.base_model)
        self.capabilities = config["capabilities"]
        self.memory = LocalMemory()
        self.network = NetworkAdapter(self.id, config)
        self.ise = ISEPClient(self.id, self.network)
        self.executer_occupation = []

        for neighbor in config["neighbours"]:
            self.network.add_neighbor(neighbor[0], neighbor[1], int(neighbor[2]))

    def decompose_task(self, task_background: str, task_question: str, user_input: str, requirement: str) -> TaskDAG:
        dag_structure, con = self.base_model.generate_task_dag(task_background, task_question, user_input, requirement)
        return dag_structure, con

    def assign_subtasks(self, task_dag: TaskDAG):
        self.executer_occupation = []
        task_allo = {}
        for index, subtask in enumerate(task_dag.subtasks):
            beacon = Beacon(
                sender=self.id,
                task_id=subtask.id,
                requirement=subtask.requirement,
                ttl=2
            )
            candidates = self.ise.broadcast_and_collect(beacon)
            best_match = self.select_executor(candidates)
            task_allo[subtask.id] = [best_match[0], subtask.to_dict()]
        
        task_allocation = TaskAllocation(task_allo)
        self.network.broadcast("task_allocation", task_allocation)
        self.ise.delegate_task(task_allo["1"][0], SubTask.from_dict(task_allo["1"][1]))

    def select_executor(self, candidates):
        # Placeholder for scoring logic
        p = random.choice(candidates)
        print(p)
        return p
        
    def evaluate_and_update(self, task_result, reward_score):
        self.lora.update_from_reward(reward_score)
        self.memory.store_result(task_result)
    
    def extract_task(self, task_description):
        prompt = f"""You are a text extractor. Your task is ONLY to separate the background information from the question in math problem statements.

Each input contains:
- Background: context, assumptions, formulas, constraints, and setup.
- Question: the final sentence or phrase that asks what needs to be found, calculated, or determined.

⚠️ IMPORTANT RULES:
- DO NOT solve or explain anything.
- DO NOT rewrite or infer any missing values.
- DO NOT modify, simplify, or expand any math expressions.
- DO NOT perform any calculations.
- DO NOT guess or assume anything.
- Only CUT the question part from the background and return both.

If the question comes after a comma, move everything after that comma to the "question".

Return your output in the following strict JSON format:
{{
  "background": "<only the setup or context>",
  "question": "<only the question sentence>"
}}

---

Example:

Input:
The perimeter of a rectangle is 24 inches. What is the number of square inches in the maximum possible area for this rectangle?

Output:
{{
  "background": "The perimeter of a rectangle is 24 inches.",
  "question": "What is the number of square inches in the maximum possible area for this rectangle?"
}}

---

Input:
If $A=2+i$, $O=-4$, $P=-i$, and $S=2+4i$, find $A-O+P+S$.

Output:
{{
  "background": "If $A=2+i$, $O=-4$, $P=-i$, and $S=2+4i$.",
  "question": "Find $A-O+P+S$"
}}

---

Now extract background and question from the following input.
Remember: do NOT solve the problem. Only extract.

Input:
{task_description}
"""

        result = self.base_model.generate(prompt)
        try:
            json_str = result.split("Output:")[1].strip()
            json_str = json_str.replace('\\', '\\\\')
            data = json.loads(json_str)
            return data["background"], data["question"], True
        except:
            return "", "", False