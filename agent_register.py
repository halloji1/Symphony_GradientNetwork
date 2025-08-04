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

        self.beacon_enabled = threading.Event()  # 控制Beacon监听
        self.beacon_enabled.set()  # 初始允许监听

        self.first_task_received = False
    
    def start(self):
        """启动监听和运行循环"""
        self.running = True
        print(f"Agent {self.agent.id} 启动，开始监听Beacon和Task...")

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
            if self.beacon_enabled.is_set():  # 仅在允许时监听
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
            try:
                sender_id, msg_type, task = self.agent.ise.receive_task(timeout=1)
                if msg_type == "task":
                    print(f"\n[任务] 收到来自 {sender_id} 的子任务")

                    if not self.first_task_received:
                        # 第一次接收到任务，开始执行
                        self.first_task_received = True

                        print("[控制] 暂停Beacon监听")
                        self.beacon_enabled.clear()

                        new_task = self.agent.execute(task)

                        if new_task.subtask_id == len(new_task.steps) + 1:  # Final result
                            final_result = new_task.final_result
                            previous_results = new_task.previous_results
                            print(final_result)
                            print("发送result给", new_task.user_id)
                            self.agent.ise.submit_result(new_task.user_id, final_result, previous_results)

                            # 当前任务结束，恢复正常
                            print("[控制] 恢复Beacon监听")
                            self.beacon_enabled.set()
                            self.first_task_received = False
                        else:
                            print("[控制] 恢复Beacon监听")
                            self.beacon_enabled.set()
                            self.first_task_received = False
                            self.agent.assign_task(new_task)  # Intermediate steps

                    else:
                        # 已有任务正在执行，转发收到的新任务
                        print(f"[中继] 当前已有任务 {self.current_task_id} 正在执行，将收到的新任务转发")
                        self.agent.assign_task(task)

            except Exception as e:
                if self.running:
                    print(f"[任务监听错误] {str(e)}")
            time.sleep(0.5)
    
    def _wait_for_stop(self):
        """等待用户输入停止命令"""
        while self.running:
            user_input = input()
            if user_input.strip().lower() == "stop":
                self.running = False
                print("\n收到停止命令，正在退出...")
                # 清理资源（如关闭网络连接）
                self.agent.network.close()
                print("服务已停止")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_num", type=int, default=1, help="config文件名")
    args = parser.parse_args()
    config_num = args.config_num

    # 配置文件路径（根据实际项目调整）
    config_path = f"./runtime/config_agent{config_num}.yaml"

    # 启动运行器
    runner = AgentRunner(config_path)
    runner.start()