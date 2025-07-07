# models/task_utils.py

import json
from typing import List, Tuple, Dict

class TaskStep:
    def __init__(self, id: str, desc: str):
        self.id = id
        self.desc = desc

    def to_dict(self):
        return {"id": self.id, "desc": self.desc}

class TaskDAG:
    def __init__(self, steps: List[TaskStep], dependencies: List[Tuple[str, str]]):
        self.steps = steps
        self.dependencies = dependencies

    def to_dict(self):
        return {
            "steps": [s.to_dict() for s in self.steps],
            "dependencies": self.dependencies
        }

    @staticmethod
    def from_dict(data: Dict) -> 'TaskDAG':
        steps = [TaskStep(s["id"], s["desc"]) for s in data.get("steps", [])]
        deps = data.get("dependencies", [])
        return TaskDAG(steps, deps)

    @staticmethod
    def from_structure(raw: Dict) -> 'TaskDAG':
        try:
            return TaskDAG.from_dict(raw)
        except Exception as e:
            print("[TaskDAG Error] Invalid DAG structure:", e)
            return TaskDAG([], [])

    def visualize(self):
        print("\nTask DAG:")
        for step in self.steps:
            print(f"  [{step.id}] {step.desc}")
        print("\nDependencies:")
        for src, dst in self.dependencies:
            print(f"  {src} -> {dst}")

# Example usage:
if __name__ == "__main__":
    # Sample data
    data = {
        "steps": [
            {"id": "1", "desc": "Read the input array"},
            {"id": "2", "desc": "Choose pivot"},
            {"id": "3", "desc": "Partition the array"},
            {"id": "4", "desc": "Recurse on subarrays"}
        ],
        "dependencies": [("1", "2"), ("2", "3"), ("3", "4")]
    }
    dag = TaskDAG.from_dict(data)
    dag.visualize()
