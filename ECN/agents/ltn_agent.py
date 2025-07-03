from models.base_loader import BaseModel
from protocol.beacon import Beacon
from core.capability import match_capability
from tools.base_tool import load_tool
from core.memory import LocalMemory

class LTNAgent:
    def __init__(self, id, model_path, sys_prompt, tools):
        self.id = id
        self.base_model = BaseModel(model_path, sys_prompt)
        self.capabilities = tools
        self.tool_modules = {tool: load_tool(tool) for tool in tools}
        self.memory = LocalMemory()

    def handle_beacon(self, beacon: Beacon):
        if match_capability(beacon.requirement, self.capabilities):
            return True
        return False

    def execute(self, task_data):
        tool_name = task_data.get("tool")
        tool = self.tool_modules.get(tool_name)
        if not tool:
            raise Exception(f"Tool '{tool_name}' not available.")
        result = tool.execute(task_data)
        self.memory.store_result(result)
        return result