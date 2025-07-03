# runtime/cli.py

import argparse
from runtime.config import load_config_from_file, get_config
from agents.fin_agent import FINAgent
from agents.ltn_agent import LTNAgent
from agents.nap_gateway import NAPGateway


def run_agent(agent_type: str, config: dict):
    model_path = config["model_path"]
    sys_prompt = "You are a helpful autonomous agent."
    capabilities = ["math", "translation", "summarization"]

    if agent_type == "FIN":
        agent = FINAgent(config["node_id"], model_path, sys_prompt, capabilities)
        print(f"[CLI] Running FIN Agent: {agent.id}")
    elif agent_type == "LTN":
        agent = LTNAgent(config["node_id"], model_path, sys_prompt, capabilities)
        print(f"[CLI] Running LTN Agent: {agent.id}")
    elif agent_type == "NAP":
        agent = NAPGateway(config["node_id"], api_interface=None)
        print(f"[CLI] Running NAP Gateway: {agent.id}")
    else:
        raise ValueError("Unknown agent type. Choose from: FIN, LTN, NAP")

    print("[CLI] Agent is live. Ready to receive tasks...")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ECN agent")
    parser.add_argument("--agent", type=str, default="FIN", help="Agent type: FIN | LTN | NAP")
    parser.add_argument("--config", type=str, default=None, help="Optional config file")

    args = parser.parse_args()
    config = load_config_from_file(args.config) if args.config else get_config()
    run_agent(args.agent, config)
