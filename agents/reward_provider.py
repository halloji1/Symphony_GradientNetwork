from models.reward_model import RewardModel
from protocol.task_contract import TaskResult

class RewardProvider:
    def __init__(self, method: str = "rule"):
        """
        初始化 RewardProvider 类
        :param method: 奖励打分方法，可选值为 "rule" | "dpo" | "grpo"
        """
        self.reward_model = RewardModel(method)

    def score_result(self, task_result: TaskResult, reference_output: str = None):
        """
        对 ComputeProvider 输出的结果进行打分
        :param task_result: 任务结果对象
        :param reference_output: 参考输出（可选）
        :return: 打分结果
        """
        task_input = task_result.output_data.get("input", "")
        model_output = task_result.output_data.get("output", "")
        score = self.reward_model.score(task_input, model_output, reference_output)
        return score