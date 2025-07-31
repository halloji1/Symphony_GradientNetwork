import time
import threading
from runtime.config import load_config_from_file
from agents.agent import Agent 
from protocol.task_contract import TaskResult, SubTask, Task
import argparse
import regex

class AgentRunner:
    def __init__(self, config_path):
        # 加载配置并初始化Agent
        self.config = load_config_from_file(config_path)
        self.agent = Agent(self.config)

        self.running = False  # 运行状态标志
    
    def start(self):
        """启动监听和运行循环"""
        self.running = True
        print(f"Agent {self.provider.id} 启动，开始监听Beacon和Task...")

        # 启动Beacon监听线程
        beacon_thread = threading.Thread(target=self._listen_beacon, daemon=True)
        beacon_thread.start()

        # 启动任务监听线程
        task_thread = threading.Thread(target=self._listen_tasks, daemon=True)
        task_thread.start()

        # 主线程等待用户输入停止命令
        self._wait_for_stop()
    
    def _listen_beacon(self):
        """持续监听Beacon并调用原类handle_beacon处理"""
        while self.running:
            try:
                # 调用ISEPClient的receive_beacon函数接收Beacon
                sender_id, msg_type, beacon = self.agent.ise.receive_beacon(timeout=1)
                if msg_type=="beacon":
                    print(f"\n[Beacon] 收到来自 {sender_id} 的Beacon请求")
                    # 调用原类的handle_beacon方法处理
                    self.agent.handle_beacon(sender_id, beacon)
            except Exception as e:
                if self.running:  # 运行中才打印错误
                    print(f"[Beacon监听错误] {str(e)}")
            time.sleep(0.5)  # 避免CPU空转
    
    def _listen_tasks(self):
        """持续监听任务并调用原类execute执行"""
        while self.running:
            sender_id, msg_type, task = self.agent.ise.receive_task(timeout=1)
            if msg_type=="task":
                print(f"\n[任务] 收到来自 {sender_id} 的子任务")
                new_task = self.agent.execute(task)
                if new_task["subtask_id"] == len(new_task["steps"])+1:
                    final_result = new_task["final_result"]
                    print(final_result)
                    print("发送result给", new_task["user_id"])
                    self.agent.ise.submit_result(new_task["user_id"], final_result)
                else:
                    requirement = new_task["steps"][new_task["subtask_id"]][1]
                    
                    self.agent.ise.delegate_task(next_executer, next_task)
                