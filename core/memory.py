# core/memory.py

import time
from collections import deque, defaultdict
from typing import Dict, List, Any

class LocalMemory:
    def __init__(self, task_limit: int = 100, neighbor_limit: int = 50):
        self.task_cache = deque(maxlen=task_limit)
        self.neighbor_data = {}  # node_id -> {capabilities, last_seen, success/failure}
        self.neighbor_scores = defaultdict(lambda: deque(maxlen=20))

    def store_result(self, result: Dict[str, Any]):
        self.task_cache.append({"timestamp": int(time.time()), **result})

    def cache_task(self, task_id: str, task_data: Dict):
        self.task_cache.append({"task_id": task_id, **task_data})

    def get_recent_tasks(self, n=5) -> List[Dict]:
        return list(self.task_cache)[-n:]

    def update_neighbor(self, node_id: str, capabilities: List[str], success: bool):
        now = int(time.time())
        if node_id not in self.neighbor_data:
            self.neighbor_data[node_id] = {"capabilities": capabilities, "last_seen": now, "score": 0.5}
        else:
            self.neighbor_data[node_id]["last_seen"] = now
            self.neighbor_data[node_id]["capabilities"] = capabilities
        self.neighbor_scores[node_id].append(1.0 if success else 0.0)

    def get_neighbors(self) -> List[str]:
        return list(self.neighbor_data.keys())

    def get_neighbor_score(self, node_id: str) -> float:
        scores = self.neighbor_scores[node_id]
        return round(sum(scores) / len(scores), 3) if scores else 0.5

    def dump(self):
        print("\n[LocalMemory Dump]")
        for task in self.task_cache:
            print("- Task:", task)
        for nid, meta in self.neighbor_data.items():
            print(f"- Neighbor {nid[:6]} | Score: {self.get_neighbor_score(nid)}")
