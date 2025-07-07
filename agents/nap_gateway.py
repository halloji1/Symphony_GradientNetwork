# agents/nap_gateway.py

from protocol.beacon import Beacon
from core.identity import generate_did

class NAPGateway:
    def __init__(self, gateway_id, api_interface):
        self.id = gateway_id
        self.did = generate_did()
        self.api = api_interface

    def receive_task(self, external_request):
        task_beacon = self._convert_to_beacon(external_request)
        self.send_to_network(task_beacon)

    def _convert_to_beacon(self, request):
        return Beacon(
            sender=self.did,
            requirement=request.get("requirement"),
            task_id=request.get("task_id"),
            ttl=2
        )

    def send_to_network(self, beacon):
        # Placeholder for network broadcast logic
        print(f"[NAP] Sending beacon to network: {beacon}")
