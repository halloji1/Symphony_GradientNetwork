# tests/test_task_contract_flow.py

from protocol.task_contract import TaskContract, TaskResult
import time

# 模拟任务分派：节点 A -> B
contract = TaskContract(
    task_id="task-001",
    assigned_to="node-B",
    input_data={"expression": "5 * (2 + 3)"},
    instructions="请计算表达式并返回结果"
)
print("[Contract Created]", contract)

# 模拟节点 B 接收任务并执行
input_expr = contract.input_data.get("expression")
try:
    result_value = eval(input_expr, {"__builtins__": None}, {})
    status = "success"
    print("[Node B Execute] 成功计算结果：", result_value)
except Exception as e:
    result_value = str(e)
    status = "fail"
    print("[Node B Execute] 计算失败：", result_value)

# 模拟回传结果
result = TaskResult(
    contract_id=contract.contract_id,
    output_data={"answer": result_value},
    status=status,
    source_id="node-B"
)
print("[Result Returned]", result)
