# soft_coordinator.py

from protocol.beacon import Beacon, BeaconResponse
from core.reputation import ReputationManager
from core.capability import match_capability
from protocol.task_contract import SubTask

class SoftCoordinator:
    def __init__(self, node_id, known_agents, reputation_db):
        self.node_id = node_id
        self.known_agents = known_agents  # List of agent metadata
        self.reputation = ReputationManager(reputation_db)

    def receive_beacon(self, beacon: Beacon):
        """
        When a beacon fails to get response from agents within timeout,
        the coordinator attempts to provide suggestions based on reputation.
        """
        matches = []
        for agent in self.known_agents:
            if match_capability(beacon.requirement, agent['capabilities']):
                score = self.reputation.get_score(agent['id'])
                matches.append((agent['id'], score))

        # Sort by reputation score
        matches = sorted(matches, key=lambda x: x[1], reverse=True)
        return [BeaconResponse(agent_id, beacon.requirement) for agent_id, _ in matches[:3]]

    def delegate_subtask(self, subtask: SubTask):
        beacon = Beacon(
            sender=self.node_id,
            task_id=subtask.id,
            requirement=subtask.requirement,
            ttl=2
        )
        suggestions = self.receive_beacon(beacon)
        return suggestions

    def update_network_state(self, agent_heartbeat):
        """Optionally used to record liveliness and update recent capabilities."""
        self.known_agents[agent_heartbeat['id']] = agent_heartbeat
