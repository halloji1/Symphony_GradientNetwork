import time
import threading
from runtime.config import load_config_from_file
from agents.user import User
import argparse
import regex
from collections import Counter
from typing import List
import json

class UserRunner:
    def __init__(self, config_path, cot_num):
        # 加载配置并初始化Agent
        self.config = load_config_from_file(config_path)
        self.user = User(self.config, cot_num)
        self.cot_num = cot_num

        self.running = False  # 运行状态标志

        self.answers = [] # Results of all tasks

        self.now_answers = [] # Results from all cots of the current task
        self.full_answers = []
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
                    self.now_answers.append(answer)
                    
                    with self.lock:
                        self.full_answers.append(result['previous_results'])
                        print(f"[Result] 当前收到 {len(self.now_answers)} 个答案")

                        if len(self.now_answers) >= self.cot_num:
                            self.final_result = self._vote_results()
                            self.answers.append(self.final_result)
                            print(f"\n✅ [Voting Result] 最终表决输出：{self.final_result}")
                            print("所有的COT如下：")
                            for x in self.full_answers:
                                print(x)
                            self.result_event.set()

            except Exception as e:
                if self.running:
                    print(f"[Result 监听错误] {str(e)}")
            time.sleep(0.2)

    def _vote_results(self):
        """对当前answers列表进行多数表决"""
        count = Counter(self.now_answers)
        most_common = count.most_common(1)[0]  # 返回格式如 ('result', 3)
        return most_common[0]
    
    def address_task(self, task_description):
        self.result_event.clear()
        self.user.assign_original_task(task_description)

        def timeout_handler():
            if not self.result_event.is_set():
                print(f"[Timeout] 任务超过5分钟未返回，标记为超时。")
                self.final_result = "[TIMEOUT]"
                self.result_event.set()
        
        timer = threading.Timer(300, timeout_handler)  # 180秒超时
        timer.start()

        print(f"等待任务的Result返回...")
        self.result_event.wait()
        timer.cancel()

        return self.final_result, self.full_answers
    
    def loop_tasks(self, tasks: List, output_path: str):
        for index, task_description in enumerate(tasks):
            self.now_answers = []
            self.full_answers = []
            self.final_result = ""
            self.address_task(task_description)

            if index%5==0:
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(self.answers, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--cot_num", type=int, default=1, help="需要投票的 CoT 答案数")
    args = parser.parse_args()
    cot_num = args.cot_num

    # 配置文件路径（根据实际项目调整）
    config_path = "./runtime/config_user.yaml"

    # 启动运行器
    runner = UserRunner(config_path, cot_num)
    runner.start()
    runner.answers = []
    task_description_1 = "How would a typical person answer each of the following questions about causation?\nLong ago, when John was only 17 years old, he got a job working for a large manufacturing company. He started out working on an assembly line for minimum wage, but after a few years at the company, he was given a choice between two line manager positions. He could stay in the woodwork division, which is where he was currently working. Or he could move to the plastics division. John was unsure what to do because he liked working in the woodwork division, but he also thought it might be worth trying something different. He finally decided to switch to the plastics division and try something new. For the last 30 years, John has worked as a production line supervisor in the plastics division. After the first year there, the plastics division was moved to a different building with more space. Unfortunately, through the many years he worked there, John was exposed to asbestos, a highly carcinogenic substance. Most of the plastics division was quite safe, but the small part in which John worked was exposed to asbestos fibers. And now, although John has never smoked a cigarette in his life and otherwise lives a healthy lifestyle, he has a highly progressed and incurable case of lung cancer at the age of 50. John had seen three cancer specialists, all of whom confirmed the worst: that, except for pain, John's cancer was untreatable and he was absolutely certain to die from it very soon (the doctors estimated no more than 2 months). Yesterday, while John was in the hospital for a routine medical appointment, a new nurse accidentally administered the wrong medication to him. John was allergic to the drug and he immediately went into shock and experienced cardiac arrest (a heart attack). Doctors attempted to resuscitate him but he died minutes after the medication was administered. Did John's job cause his premature death?\nOptions:\n- Yes\n- No"
    tasks = [task_description_1]
    runner.loop_tasks(tasks=tasks, output_path="/workspace/Symphony_GradientNetwork/bbh.json")


    try:
        while True:
            time.sleep(1)  # 持续运行，等待结果监听
    except KeyboardInterrupt:
        print("程序被手动终止")
        runner.running = False  # 停止守护线程的循环
