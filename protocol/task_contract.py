# protocol/task_contract.py

import uuid
import time
from typing import Dict, Any, List, Tuple

class TaskContract:
    def __init__(self, task_id: int, assigned_to: str, original_problem: str, previous_results: list, instructions: str, decomposed: bool):
        self.contract_id = str(uuid.uuid4())
        self.task_id = task_id
        self.assigned_to = assigned_to
        self.original_problem = original_problem
        self.previous_results = previous_results
        self.instructions = instructions
        self.decomposed = decomposed
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        return {
            "contract_id": self.contract_id,
            "task_id": self.task_id,
            "assigned_to": self.assigned_to,
            "original_problem": self.original_problem,
            "previous_results": self.previous_results,
            "instructions": self.instructions,
            "decomposed": self.decomposed,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TaskContract':
        return TaskContract(
            task_id=data["task_id"],
            assigned_to=data["assigned_to"],
            original_problem=data["original_problem"],
            previous_results=data["previous_results"],
            instructions=data["instructions"],
            decomposed=data["decomposed"]
        )

    def __repr__(self):
        return f"<Contract {self.contract_id[:6]} for {self.assigned_to} | Task: {self.task_id[:6]}>"


class TaskResult:
    def __init__(self, target_id, executer_id, result):
        self.target_id = target_id
        self.executer_id = executer_id
        self.result = result

    def to_dict(self) -> Dict:
        return {
            "target_id": self.target_id,
            "executer_id": self.executer_id,
            "result": self.result
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TaskResult':
        return TaskResult(
            task_id=data["task_id"],
            executer_id=data["executer_id"],
            result=data["result"],
        )

    def __repr__(self):
        return f"<Result {self.contract_id[:6]} from {self.source_id} | Status: {self.status}>"

class TaskAllocation:
    def __init__(self, task_allocation: Dict):
        self.task_allocation = task_allocation

    def to_dict(self):
        return self.task_allocation
    
    @staticmethod
    def from_dict(data):
        return data
    
    def __repr__(self):
        return f"<Result {self.contract_id[:6]} from {self.source_id} | Status: {self.status}>"


class SubTask:
    def __init__(self, id: str = None, requirement: str = "", original_problem: str = "", previous_results: list = [], instructions: str = "", decomposed: bool = True):
        """
        初始化 SubTask 类。

        :param id: 子任务的唯一标识符。
        :param requirement: 子任务的能力要求描述。
        :param original_problem: 原始任务。
        :param previous_results: 前序子任务的结果。
        :param instructions: 子任务的执行指令。
        """
        self.id = id
        self.requirement = requirement
        self.original_problem = original_problem
        self.previous_results = previous_results
        self.instructions = instructions
        self.decomposed = decomposed

    def to_dict(self) -> Dict:
        """
        将 SubTask 对象转换为字典形式。

        :return: 包含子任务信息的字典。
        """
        return {
            "id": self.id,
            "requirement": self.requirement,
            "original_problem": self.original_problem,
            "previous_results": self.previous_results,
            "instructions": self.instructions,
            "decomposed": self.decomposed
        }

    @staticmethod
    def from_dict(data: Dict) -> 'SubTask':
        """
        从字典数据中创建 SubTask 对象。

        :param data: 包含子任务信息的字典。
        :return: SubTask 对象。
        """
        return SubTask(
            id=data.get("id"),
            requirement=data.get("requirement", ""),
            original_problem=data.get("original_problem", ""),
            previous_results=data.get("previous_results", []),
            instructions=data.get("instructions", ""),
            decomposed=data.get("decomposed", True)
        )

    def __repr__(self):
        """
        返回 SubTask 对象的字符串表示形式。

        :return: 子任务的字符串表示。
        """
        return f"<SubTask {self.id[:8]}: {self.requirement}>"


class TaskDAG:
    def __init__(self, steps: List[SubTask], dependencies: List[Tuple[str, str]]):
        """
        初始化 TaskDAG 类。

        :param steps: 子任务列表。
        :param dependencies: 子任务之间的依赖关系列表。
        """
        self.subtasks = steps
        self.dependencies = dependencies

    def to_dict(self) -> Dict:
        """
        将 TaskDAG 对象转换为字典形式。

        :return: 包含任务 DAG 信息的字典。
        """
        return {
            "steps": [s.to_dict() for s in self.subtasks],
            "dependencies": self.dependencies
        }

    @staticmethod
    def from_dict(data: Dict) -> 'TaskDAG':
        """
        从字典数据中创建 TaskDAG 对象。

        :param data: 包含任务 DAG 信息的字典。
        :return: TaskDAG 对象。
        """
        steps = [SubTask.from_dict(s) for s in data.get("steps", [])]
        deps = data.get("dependencies", [])
        return TaskDAG(steps, deps)

    @staticmethod
    def from_structure(raw: Dict) -> 'TaskDAG':
        """
        从原始数据结构中创建 TaskDAG 对象。

        :param raw: 原始数据结构。
        :return: TaskDAG 对象。
        """
        try:
            return TaskDAG.from_dict(raw)
        except Exception as e:
            print("[TaskDAG Error] Invalid DAG structure:", e)
            return TaskDAG([], [])

    def visualize(self):
        """
        可视化任务 DAG 的结构。
        """
        print("\nTask DAG:")
        for step in self.subtasks:
            print(f"  [{step.id}] {step.requirement}")
        print("\nDependencies:")
        for src, dst in self.dependencies:
            print(f"  {src} -> {dst}")

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