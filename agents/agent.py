from models.base_loader import BaseModel
from protocol.beacon import Beacon
from protocol.response import BeaconResponse
from models.lora_manager import LoRAAdapter
from core.capability import CapabilityManager
from core.memory import LocalMemory
from protocol.task_contract import TaskResult, Task
from infra.ISEP import ISEPClient
from infra.network_adapter import NetworkAdapter

class Agent:
    def __init__(self, config):
        self.id = config["node_id"]
        self.gpu_id = config.get("gpu_id", 0)
        self.sys_prompt = config["sys_prompt"]
        if config["base_model"] == "test":
            self.base_model = None
        else:
            self.base_model = BaseModel(config["base_model"], config["sys_prompt"], device=f"cuda:{self.gpu_id}")
            self.lora = LoRAAdapter(self.base_model)
        self.capabilities = config["capabilities"]
        self.memory = LocalMemory()
        self.capab_manager = CapabilityManager(self.capabilities)
        self.network = NetworkAdapter(self.id, config)
        self.ise = ISEPClient(self.id, self.network)
        
        for neighbor in config["neighbours"]:
            self.network.add_neighbor(neighbor[0], neighbor[1], int(neighbor[2]))
        
    def execute(self, task: Task):
        if task["subtask_id"] == 0: # decompose task
            user_input = task["original_problem"]
            task_background, task_question, con_1 = self.base_model.extract_task(user_input)
            if con_1:
                steps, con_2 = self.base_model.generate_task_dag(task_background, task_question, user_input, "math")
                if con_2:
                    task["steps"] = steps
                    print(task["steps"])
            task["subtask_id"] += 1
            return Task.from_dict(task)
        else:  # execute subtask
            instruction = task["steps"][str(task["subtask_id"])][0]
            previous_results = task["previous_results"]
            pres = " ".join(previous_results)
            task_description = f"{self.sys_prompt}\nBackground information include: \"{pres}\". Based on the background information, solve the sub-task: \"{instruction}\". Provide the final answer formatted as $\\boxed{{<Answer>}}$. Do not provide additional explanations or code."
            
            raw_result = self.base_model.generate(task_description)
            
            pos = raw_result.find("DO NOT")
            if pos!=-1:
                raw_result = raw_result[:pos].strip()

            result = raw_result.split("Output:")[1].strip()
            
            task["previous_results"].append(f"{instruction} Answer: {result}")
            if task["subtask_id"] == len(task["steps"]):
                task["final_result"] = result
            task["subtask_id"] += 1
            return Task.from_dict(task)
    
    def assign_task(self, task: Task):
        beacon = Beacon(sender=self.id, task_id=str(task.subtask_id), requirement=task.steps[str(task.subtask_id)][1], ttl=2)
        candidates = self.ise.broadcast_and_collect(beacon)
        best_matches = self.select_executor(candidates, 1)
        print(best_matches)
        
        for match in best_matches:
            self.ise.delegate_task(match[0], task)
    
    def select_executor(self, candidates, num):
        candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
        for i in range(len(candidates)):
            candidate = candidates[i]
            if candidate[0] == self.id:
                if candidate[1] == candidates[0][1]:
                    candidates[i] = candidates[0]
                    candidates[0] = candidate
                    break
        return candidates[:num]
    
    def handle_beacon(self, sender_id: str, beacon: Beacon):
        # 计算能力得分
        score = self.capab_manager.match(beacon["requirement"])
        # 创建 BeaconResponse
        response = BeaconResponse(self.id, beacon["task_id"], match_score=score)
        # 发送响应
        self.ise.send_response(sender_id, "beacon_response", response)
