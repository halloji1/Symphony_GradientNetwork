# tests/test_beacon_exchange.py

from protocol.beacon import Beacon
from protocol.response import BeaconResponse
from core.capability import CapabilityManager
import time

# 模拟 A 节点广播 Beacon
sender_id = "node-A"
beacon = Beacon(sender=sender_id, requirement="math", ttl=2)
print("[Beacon Broadcast]", beacon)

# 模拟 B 节点接收并匹配能力
responder_id = "node-B"
capability_b = CapabilityManager(["math", "translation"])
score = capability_b.match(beacon.requirement)

if score > 0.5:
    response = BeaconResponse(
        responder_id=responder_id,
        capabilities=capability_b.list_capabilities(),
        match_score=score,
        estimate_cost=0.2
    )
    print("[Beacon Response]", response)
else:
    print(f"[Node {responder_id}] No match for: {beacon.requirement}")

# 模拟 C 节点未匹配成功
responder_c = "node-C"
capability_c = CapabilityManager(["image", "style-transfer"])
score_c = capability_c.match(beacon.requirement)

if score_c > 0.5:
    print("[Node C] Should not match, but matched unexpectedly")
else:
    print(f"[Node {responder_c}] No match for: {beacon.requirement}")
