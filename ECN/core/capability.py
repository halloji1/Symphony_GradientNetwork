# core/capability.py

from typing import List
import difflib

class CapabilityManager:
    def __init__(self, capability_tags: List[str]):
        self.capabilities = list(set([t.lower() for t in capability_tags]))

    def add_capability(self, tag: str):
        tag = tag.lower()
        if tag not in self.capabilities:
            self.capabilities.append(tag)

    def remove_capability(self, tag: str):
        tag = tag.lower()
        if tag in self.capabilities:
            self.capabilities.remove(tag)

    def list_capabilities(self) -> List[str]:
        return self.capabilities

    def match(self, requirement: str, threshold: float = 0.5) -> float:
        """
        Returns a similarity score between 0.0 ~ 1.0
        """
        requirement = requirement.lower()
        best_score = 0.0
        for tag in self.capabilities:
            ratio = difflib.SequenceMatcher(None, tag, requirement).ratio()
            best_score = max(best_score, ratio)
        return round(best_score, 3)

    def match_and_filter(self, requirement: str, threshold: float = 0.5) -> bool:
        return self.match(requirement, threshold=threshold) >= threshold


# 示例
if __name__ == "__main__":
    cm = CapabilityManager(["image-to-text", "style-transfer", "translation"])
    print("Declared:", cm.list_capabilities())
    print("Match 'image translation':", cm.match("image translation"))
    print("Should accept?", cm.match_and_filter("image translation", threshold=0.6))
