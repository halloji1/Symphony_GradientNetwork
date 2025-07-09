# protocol/task_contract.py

import uuid
import time
from typing import Dict, Any, List, Tuple

class TaskContract:
    def __init__(self, task_id: str, assigned_to: str, input_data: Dict[str, Any], instructions: str):
        self.contract_id = str(uuid.uuid4())
        self.task_id = task_id
        self.assigned_to = assigned_to
        self.input_data = input_data
        self.instructions = instructions
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        return {
            "contract_id": self.contract_id,
            "task_id": self.task_id,
            "assigned_to": self.assigned_to,
            "input_data": self.input_data,
            "instructions": self.instructions,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TaskContract':
        return TaskContract(
            task_id=data["task_id"],
            assigned_to=data["assigned_to"],
            input_data=data["input_data"],
            instructions=data["instructions"]
        )

    def __repr__(self):
        return f"<Contract {self.contract_id[:6]} for {self.assigned_to} | Task: {self.task_id[:6]}>"


class TaskResult:
    def __init__(self, contract_id: str, output_data: Dict[str, Any], status: str, source_id: str):
        self.contract_id = contract_id
        self.output_data = output_data
        self.status = status  # "success" | "fail" | "partial"
        self.source_id = source_id
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        return {
            "contract_id": self.contract_id,
            "output_data": self.output_data,
            "status": self.status,
            "source_id": self.source_id,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'TaskResult':
        return TaskResult(
            contract_id=data["contract_id"],
            output_data=data["output_data"],
            status=data["status"],
            source_id=data["source_id"]
        )

    def __repr__(self):
        return f"<Result {self.contract_id[:6]} from {self.source_id} | Status: {self.status}>"


class SubTask:
    def __init__(self, id: str = None, requirement: str = "", input_data: Dict = None, instructions: str = ""):
        """
        初始化 SubTask 类。

        :param id: 子任务的唯一标识符。
        :param requirement: 子任务的能力要求描述。
        :param input_data: 子任务的输入数据。
        :param instructions: 子任务的执行指令。
        """
        self.id = id or str(uuid.uuid4())
        self.requirement = requirement
        self.input_data = input_data or {}
        self.instructions = instructions

    def to_dict(self) -> Dict:
        """
        将 SubTask 对象转换为字典形式。

        :return: 包含子任务信息的字典。
        """
        return {
            "id": self.id,
            "requirement": self.requirement,
            "input_data": self.input_data,
            "instructions": self.instructions
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
            input_data=data.get("input_data", {}),
            instructions=data.get("instructions", "")
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