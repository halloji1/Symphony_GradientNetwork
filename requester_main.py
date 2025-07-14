# 在 TaskRequester 代码中添加测试逻辑
from agents.task_requester import TaskRequester
from runtime.config import load_config_from_file

# 加载配置文件
config = load_config_from_file('./runtime/config_task_requester.yaml')

# 创建 TaskRequester 实例
task_requester = TaskRequester(config)

# 定义要解决的问题
task_description = "翻译一段英文文本，然后对翻译结果进行总结"

# TaskRequester 分解任务
task_dag = task_requester.decompose_task(task_description)

# TaskRequester 分配子任务
task_requester.assign_subtasks(task_dag)