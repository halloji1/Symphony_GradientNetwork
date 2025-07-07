# models/reward_model.py

import random
from typing import Dict, Optional

class RewardModel:
    def __init__(self, method: str = "rule"):
        """
        method: "rule" | "dpo" | "grpo"
        """
        self.method = method

    def score(self, task_input: str, model_output: str, reference_output: Optional[str] = None) -> float:
        if self.method == "rule":
            return self._rule_based_score(task_input, model_output)
        elif self.method == "dpo":
            return self._dpo_pairwise_score(model_output, reference_output)
        elif self.method == "grpo":
            return self._grpo_group_score(task_input, model_output)
        else:
            raise ValueError("Unsupported reward method")

    def _rule_based_score(self, task_input: str, output: str) -> float:
        # Simple rule: longer answers with matching keywords get higher score
        keywords = ["step", "result", "complete"]
        match_score = sum(1 for kw in keywords if kw in output.lower())
        length_score = min(len(output) / 100, 1.0)
        score = 0.4 * match_score / len(keywords) + 0.6 * length_score
        return round(score, 3)

    def _dpo_pairwise_score(self, output: str, reference: str) -> float:
        # Placeholder: give higher score if output shares more tokens with reference
        output_set = set(output.split())
        reference_set = set(reference.split())
        overlap = output_set & reference_set
        return round(len(overlap) / max(len(reference_set), 1), 3)

    def _grpo_group_score(self, task_input: str, output: str) -> float:
        # Placeholder: random variation to simulate group consensus
        base_score = self._rule_based_score(task_input, output)
        noise = random.uniform(-0.05, 0.05)
        return round(min(max(base_score + noise, 0), 1), 3)