# protocol/beacon.py

import uuid
import time
from typing import Dict

class Beacon:
    def __init__(self, sender: str, requirement: str, task_id: str = None, ttl: int = 2):
        self.beacon_id = str(uuid.uuid4())
        self.sender = sender              # 发出此信标的节点 DID
        self.task_id = task_id or self.beacon_id
        self.requirement = requirement    # 对能力的简要描述
        self.ttl = ttl                    # 剩余传播跳数（用于范围控制）
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        return {
            "beacon_id": self.beacon_id,
            "sender": self.sender,
            "task_id": self.task_id,
            "requirement": self.requirement,
            "ttl": self.ttl,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict) -> 'Beacon':
        beacon = Beacon(
            sender=data.get("sender", "unknown"),
            requirement=data.get("requirement", ""),
            task_id=data.get("task_id"),
            ttl=data.get("ttl", 2)
        )
        beacon.beacon_id = data.get("beacon_id", str(uuid.uuid4()))
        beacon.timestamp = data.get("timestamp", int(time.time()))
        return beacon

    def __repr__(self):
        return f"<Beacon {self.task_id[:8]} from {self.sender} need '{self.requirement}' TTL={self.ttl}>"

