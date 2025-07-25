import argparse
from runtime.config import load_config_from_file, get_config
from agents.task_requester import TaskRequester
from agents.compute_provider import ComputeProvider
from agents.nap_gateway import NAPGateway

def run_agent(agent_type: str, config: dict):
    gpu_ids = config.get("gpu_ids", [0])
    for i, gpu_id in enumerate(gpu_ids):
        new_config = config.copy()
        new_config["gpu_id"] = gpu_id
        new_config["node_id"] = f"{config['node_id']}-{i}"  # 为每个agent分配唯一的node_id

        if agent_type == "TaskRequester":
            agent = TaskRequester(new_config)
            print(f"[CLI] Running TaskRequester Agent: {agent.id} on GPU {gpu_id}")
        elif agent_type == "ComputeProvider":
            agent = ComputeProvider(new_config)
            print(f"[CLI] Running ComputeProvider Agent: {agent.id} on GPU {gpu_id}")
        elif agent_type == "NAP":
            agent = NAPGateway(new_config["node_id"], api_interface=None)
            print(f"[CLI] Running NAP Gateway: {agent.id} on GPU {gpu_id}")
        else:
            raise ValueError("Unknown agent type. Choose from: TaskRequester, ComputeProvider, NAP")

        print("[CLI] Agent is live. Ready to receive tasks...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Symphony agent")
    parser.add_argument("--agent", type=str, default="TaskRequester", help="Agent type: TaskRequester | ComputeProvider | NAP")
    parser.add_argument("--config", type=str, default=None, help="Optional config file")

    args = parser.parse_args()
    config = load_config_from_file(args.config) if args.config else get_config()
    run_agent(args.agent, config)