# protocol/task_contract.py

import uuid
import time
from typing import Dict, Any, List, Tuple

class TaskResult:
    def __init__(self, target_id, executer_id, result, previous_results):
        self.target_id = target_id
        self.executer_id = executer_id
        self.result = result
        self.previous_results = previous_results

    def to_dict(self) -> Dict:
        return {
            "target_id": self.target_id,
            "executer_id": self.executer_id,
            "result": self.result,
            "previous_results": self.previous_results
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TaskResult':
        return TaskResult(
            task_id=data["task_id"],
            executer_id=data["executer_id"],
            result=data["result"],
            previous_results=data["previous_results"]
        )

    def __repr__(self):
        return f"<Result {self.contract_id[:6]} from {self.source_id} | Status: {self.status}>"

class Task:
    def __init__(self, subtask_id: int, steps: Dict, previous_results: List, original_problem: str, final_result: str, user_id: str):
        """
        初始化Task类
        subtask_id: 当前子任务的序号
        steps: 包含每个步骤的instruction以及requirement的字典
        previous_results: 前序任务的描述以及结果
        original_problem: 用户输入的原文
        final_result: 最终结果
        user_id: 用户id
        """
        self.subtask_id = subtask_id
        self.steps = steps
        self.previous_results = previous_results
        self.original_problem = original_problem
        self.final_result = final_result
        self.user_id = user_id
    
    def to_dict(self) -> Dict:
        """
        将 Task 对象转换为字典形式，从而能够以json的形式发送
        """
        return {
            "subtask_id": self.subtask_id,
            "steps": self.steps,
            "previous_results": self.previous_results,
            "original_problem": self.original_problem,
            "final_result": self.final_result,
            "user_id": self.user_id
        }
    
    @staticmethod
    def from_dict(data: Dict) -> 'Task':
        return Task(subtask_id = data["subtask_id"],
                    steps = data["steps"],
                    previous_results = data["previous_results"],
                    original_problem = data["original_problem"],
                    final_result = data["final_result"],
                    user_id = data["user_id"])
    
    def __repr__(self):
        if self.subtask_id == 0:
            return f"<Subtask {self.subtask_id}: Generate plan"
        else:
            return f"<Subtask {self.subtask_id}: {self.steps[self.subtask_id]}"