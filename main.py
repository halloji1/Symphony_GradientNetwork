import argparse
from runtime.config import load_config_from_file, get_config
from runtime.cli import run_agent

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Symphony agent")
    parser.add_argument("--agent", type=str, default="TaskRequester", help="Agent type: TaskRequester | ComputeProvider | NAP")
    parser.add_argument("--config", type=str, default=None, help="Optional config file")

    args = parser.parse_args()
    config = load_config_from_file(args.config) if args.config else get_config()
    run_agent(args.agent, config)