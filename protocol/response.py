# protocol/response.py

import uuid
import time
from typing import Dict, Optional

class BeaconResponse:
    def __init__(self, responder_id: str, task_id: str, match_score: float = 1.0, estimate_cost: float = 1.0):
        self.response_id = str(uuid.uuid4())
        self.responder_id = responder_id        # 当前节点 ID
        self.task_id = task_id        # 节点声明的能力列表
        self.match_score = round(match_score, 3) # 与任务要求的匹配分数 (0.0 ~ 1.0)
        self.estimate_cost = round(estimate_cost, 3)  # 执行任务的估算代价
        self.timestamp = int(time.time())

    def to_dict(self) -> Dict:
        return {
            "response_id": self.response_id,
            "responder_id": self.responder_id,
            "task_id": self.task_id,
            "match_score": self.match_score,
            "estimate_cost": self.estimate_cost,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict) -> 'BeaconResponse':
        resp = BeaconResponse(
            responder_id=data.get("responder_id", "unknown"),
            task_id=data.get("task_id", []),
            match_score=data.get("match_score", 1.0),
            estimate_cost=data.get("estimate_cost", 1.0)
        )
        resp.response_id = data.get("response_id", str(uuid.uuid4()))
        resp.timestamp = data.get("timestamp", int(time.time()))
        return resp

    def __repr__(self):
        return f"<Response {self.response_id[:6]} from {self.responder_id}, score={self.match_score}, cost={self.estimate_cost}>"
