# core/reputation.py

from collections import defaultdict, deque
import time

class ReputationManager:
    def __init__(self, max_records: int = 50):
        self.reputation_history = defaultdict(lambda: deque(maxlen=max_records))  # node_id -> deque of scores
        self.last_update = {}  # node_id -> timestamp

    def update_score(self, node_id: str, score: float):
        now = int(time.time())
        score = max(0.0, min(1.0, score))  # ensure bounded [0, 1]
        self.reputation_history[node_id].append(score)
        self.last_update[node_id] = now

    def get_trust_score(self, node_id: str) -> float:
        scores = self.reputation_history[node_id]
        if not scores:
            return 0.5  # neutral default
        decay = 0.95
        weighted_sum = sum(score * (decay ** i) for i, score in enumerate(reversed(scores)))
        normalizer = sum((decay ** i) for i in range(len(scores)))
        return round(weighted_sum / normalizer, 3)

    def get_all_scores(self) -> dict:
        return {nid: self.get_trust_score(nid) for nid in self.reputation_history.keys()}

    def dump(self):
        print("\n[Reputation Dump]")
        for nid, scores in self.reputation_history.items():
            print(f"- Node {nid[:6]}: Trust = {self.get_trust_score(nid)}")