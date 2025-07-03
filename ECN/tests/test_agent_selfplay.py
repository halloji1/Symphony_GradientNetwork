from tools.tool_math import MathTool
from protocol.task_contract import TaskContract, TaskResult

# 一个模拟的自对抗任务：agent 自拟数学任务并尝试求解
proposer_id = "self-agent"
tool = MathTool()
task_expr = "(3 + 4) * 2"

# 模拟构造任务
contract = TaskContract(
    task_id="self-task-1",
    assigned_to=proposer_id,
    input_data={"expression": task_expr},
    instructions="请求解此表达式"
)
print("[SelfPlay Task Generated]", contract)

# 作为 solver 直接调用 tool
answer = tool.run(task_expr)
print("[Solver Result]", answer)

# 模拟内部反馈回环
result = TaskResult(
    contract_id=contract.contract_id,
    output_data={"answer": answer},
    status="success",
    source_id=proposer_id
)
print("[SelfPlay Feedback]", result)
