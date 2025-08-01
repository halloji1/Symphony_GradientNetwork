import time
import threading
from runtime.config import load_config_from_file
from protocol.task_contract import TaskResult, SubTask, Task
from agents.user import User
import argparse
import regex
from collections import Counter

class UserRunner:
    def __init__(self, config_path, cot_num):
        # 加载配置并初始化Agent
        self.config = load_config_from_file(config_path)
        self.user = User(self.config, cot_num)
        self.cot_num = cot_num

        self.running = False  # 运行状态标志

        self.answers = []
        self.result_event = threading.Event()
        self.lock = threading.Lock()  # 用于多线程安全添加结果
        self.final_result = ""
    
    def start(self):
        """启动监听和运行循环"""
        self.running = True
        print(f"User {self.user.id} 启动，开始监听Result...")

        # 启动Result监听线程
        result_thread = threading.Thread(target=self._listen_result, daemon=True)
        result_thread.start()
    
    def _listen_result(self):
        """持续监听Result并处理结果"""
        while self.running:
            try:
                sender_id, msg_type, result = self.user.ise.receive_result(timeout=1)
                if msg_type == "task_result":
                    print(f"\n[Result] 收到来自 {sender_id} 的Result")
                    answer = result["result"]
                    
                    with self.lock:
                        self.answers.append(answer)
                        print(f"[Result] 当前收到 {len(self.answers)} 个答案")

                        if len(self.answers) >= self.cot_num:
                            self.final_result = self._vote_results()
                            print(f"\n✅ [Voting Result] 最终表决输出：{self.final_result}")
                            self.result_event.set()

            except Exception as e:
                if self.running:
                    print(f"[Beacon监听错误] {str(e)}")
            time.sleep(0.2)

    def _vote_results(self):
        """对当前answers列表进行多数表决"""
        count = Counter(self.answers)
        most_common = count.most_common(1)[0]  # 返回格式如 ('result', 3)
        return most_common[0]
    
    def address_task(self, task_description):
        self.result_event.clear()
        self.user.assign_original_task(task_description)

        def timeout_handler():
            if not self.result_event.is_set():
                print(f"[Timeout] 任务超过5分钟未返回，标记为超时。")
                self.now_result = "[TIMEOUT]"
                self.result_event.set()
        
        timer = threading.Timer(300, timeout_handler)  # 180秒超时
        timer.start()

        print(f"等待任务的Result返回...")
        self.result_event.wait()
        timer.cancel()

        return self.final_result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cot_num", type=int, default=3, help="需要投票的 CoT 答案数")
    args = parser.parse_args()
    cot_num = args.cot_num

    # 配置文件路径（根据实际项目调整）
    config_path = "./runtime/config_user.yaml"

    # 启动运行器
    runner = UserRunner(config_path, cot_num)
    runner.start()
    runner.answers = []
    task_description = "What is the positive difference between $120\\%$ of 30 and $130\\%$ of 20?"
    runner.address_task(task_description)

    try:
        while True:
            time.sleep(1)  # 持续运行，等待结果监听
    except KeyboardInterrupt:
        print("程序被手动终止")
        runner.running = False  # 停止守护线程的循环