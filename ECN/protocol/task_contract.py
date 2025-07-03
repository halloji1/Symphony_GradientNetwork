# protocol/task_contract.py

import uuid
import time
from typing import Dict, Any

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