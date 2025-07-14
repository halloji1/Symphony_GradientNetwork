# 在 TaskRequester 代码中添加测试逻辑
from agents.task_requester import TaskRequester
from runtime.config import load_config_from_file


from protocol.task_contract import SubTask, TaskDAG

# 创建子任务
task1 = SubTask(
    id="prepare_data",
    requirement="翻译",
    input_data={"word": "apple", "source_lang": "en", "target_lang": "zh"},
    instructions="格式化待翻译文本"
)

task2 = SubTask(
    id="translate",
    requirement="翻译",
    input_data={
    },
    instructions="调用翻译API将文本从英语翻译成中文"
)

# 定义依赖关系
dependencies = [
]

# 创建任务DAG
task_dag = TaskDAG(
    steps=[task1, task2],
    dependencies=dependencies
)


# 加载配置文件
config = load_config_from_file('./runtime/config.yaml')

# 创建 TaskRequester 实例
task_requester = TaskRequester(config)



# 定义要解决的问题
task_description = "翻译一段英文文本，然后对翻译结果进行总结"

# TaskRequester 分解任务
# task_dag = task_requester.decompose_task(task_description)

# TaskRequester 分配子任务
task_requester.assign_subtasks(task_dag)