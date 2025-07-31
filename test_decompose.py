# 在 TaskRequester 代码中添加测试逻辑
from agents.task_requester import TaskRequester
from runtime.config import load_config_from_file
import time
import threading
from runtime.config import load_config_from_file
from protocol.task_contract import TaskResult, SubTask
from protocol.task_contract import SubTask, TaskDAG
import json
import os

class TaskRequesterRunner:
    def __init__(self, config_path):
        # 加载配置并初始化原ComputeProvider（不修改其代码）
        self.config = load_config_from_file(config_path)
        self.requester = TaskRequester(self.config)  # 原类实例

        self.running = False  # 运行状态标志

        self.answers = []
        self.result_event = threading.Event()
        self.now_result = ""

    def start(self):
        """启动监听和运行循环"""
        self.running = True
        print(f"[Runner] TaskRequester {self.requester.id} 启动，开始监听Result...")

        # 启动Result监听线程
        result_thread = threading.Thread(target=self._listen_result, daemon=True)
        result_thread.start()

    def _listen_result(self):
        """持续监听Result并调用原类handle_result处理"""
        while self.running:
            try:
                # 调用ISEPClient的receive_beacon函数接收Beacon
                sender_id, msg_type, result = self.requester.ise.receive_result(timeout=1)
                if msg_type=="task_result":
                    print(f"\n[Result] 收到来自 {sender_id} 的Result")
                    self.now_result = result["result"]
                    self.result_event.set()
                    
            except Exception as e:
                if self.running:  # 运行中才打印错误
                    print(f"[Beacon监听错误] {str(e)}")
            time.sleep(0.5)  # 避免CPU空转
        
    def assign_subtask(self, task_dag):
        self.requester.assign_subtasks(task_dag)
    
    def load_task(self, task_path, task_name):
        with open(task_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "task_name": task_name,
            "problem": data["problem"],
            "solution": data["solution"],
            "model_output": ""
        }

    def solve_problems(self, output_path, root_path):
        folders = ['algebra']
        for folder in folders:
            folder_path = os.path.join(root_path, folder)
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
            for index, file in enumerate(files):
                task_name = f"{folder}_{file}"
                file_path = os.path.join(folder_path, file)
                task = self.load_task(file_path, task_name)
                task_description = task["problem"]
                task_background, task_question, con_1 = self.requester.extract_task(task_description)
                if con_1:
                    task_dag, con_2 = self.requester.decompose_task(task_background, task_question, task_description, "math")

                    if con_2:
                        self.result_event.clear()
                        self.assign_subtask(task_dag)

                        def timeout_handler():
                            if not self.result_event.is_set():
                                print(f"[Timeout] 任务 {task_name} 超过5分钟未返回，标记为超时。")
                                self.now_result = "[TIMEOUT]"
                                self.result_event.set()
                        
                        timer = threading.Timer(300, timeout_handler)  # 180秒超时
                        timer.start()

                        print(f"[Runner] 等待任务 {task_name} 的Result返回...")
                        self.result_event.wait()
                        timer.cancel()

                        if self.now_result!="":
                            task["model_output"] = self.now_result
                            self.now_result = ""
                            self.answers.append(task)
                            print(f"[Runner] 任务 {task_name} 完成，继续下一个。")
                
                if index % 5 == 0:
                    with open(output_path, "w", encoding="utf-8") as f:
                        json.dump(self.answers, f, ensure_ascii=False, indent=2)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.answers, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    # 配置文件路径（根据实际项目调整）
    config_path = "./runtime/config_task.yaml"

    # 启动运行器
    runner = TaskRequesterRunner(config_path)
    runner.start()
    
    task_description = ""
    task_background, task_question, con_1 = runner.requester.extract_task(task_description)
    task_dag, con_2 = runner.requester.decompose_task(task_background, task_question, task_description, "math")