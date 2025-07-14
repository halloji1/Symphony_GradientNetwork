from agents.task_requester import TaskRequester
from agents.compute_provider import ComputeProvider
from protocol.task_contract import TaskDAG, SubTask
from prompts.roles_prompt import TASK_REQUESTER_PROMPT


# 定义要解决的问题
task_description = "翻译一段英文文本，然后对翻译结果进行总结"

# TaskRequester 分解任务
task_dag = task_requester.decompose_task(task_description)

# 打印分解后的任务 DAG
task_dag.visualize()

# TaskRequester 分配子任务
task_requester.assign_subtasks(task_dag)

# ComputeProvider 处理接收到的子任务
# 这里假设通过某种机制（如消息队列）将子任务传递给 ComputeProvider
for subtask in task_dag.subtasks:
    result = compute_provider.execute(subtask)
    if result:
        print(f"子任务 {subtask.id} 执行结果: {result}")
    else:
        print(f"子任务 {subtask.id} 执行失败")