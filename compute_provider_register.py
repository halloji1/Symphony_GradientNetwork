import time
import threading
from runtime.config import load_config_from_file
from agents.compute_provider import ComputeProvider  # 导入原ComputeProvider类
from protocol.task_contract import TaskResult, SubTask
import argparse
import regex

class ComputeProviderRunner:
    def __init__(self, config_path):
        # 加载配置并初始化原ComputeProvider（不修改其代码）
        self.config = load_config_from_file(config_path)
        self.provider = ComputeProvider(self.config)  # 原类实例

        self.running = False  # 运行状态标志

    def start(self):
        """启动监听和运行循环"""
        self.running = True
        print(f"[Runner] ComputeProvider {self.provider.id} 启动，开始监听Beacon和任务...")

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
                sender_id, msg_type, beacon = self.provider.ise.receive_beacon(timeout=1)
                if msg_type=="beacon":
                    print(f"\n[Beacon] 收到来自 {sender_id} 的Beacon请求")
                    # 调用原类的handle_beacon方法处理
                    self.provider.handle_beacon(sender_id, beacon)
            except Exception as e:
                if self.running:  # 运行中才打印错误
                    print(f"[Beacon监听错误] {str(e)}")
            time.sleep(0.5)  # 避免CPU空转

    def _listen_tasks(self):
        """持续监听任务并调用原类execute执行"""
        while self.running:
            # try:
            # 假设通过network/ise接收任务（根据原类属性调整）
            sender_id, msg_type, subtask = self.provider.ise.receive_task(timeout=1)
            if msg_type=="subtask":
                description = subtask["instructions"]
                task_ids = list(self.provider.ise.task_allocation.keys())
                
                print(f"\n[任务] 收到来自 {sender_id} 的子任务: ")

                if str(subtask["task_id"]) != str(task_ids[-1]):
                    # 调用原类的execute方法执行任务
                    result = self.provider.execute(subtask)
                    print(result)
                
                    next_task_id = str(int(subtask["task_id"])+1)
                    next_executer = self.provider.ise.task_allocation[next_task_id][0]
                    next_task_dict = self.provider.ise.task_allocation[next_task_id][1]
                    next_task = SubTask.from_dict(next_task_dict)
                    next_task.previous_results = subtask["previous_results"]
                    next_task.previous_results.append(f"{description} Answer: {result}")
                    # print(next_task.previous_results)
                    self.provider.ise.delegate_task(next_executer, next_task)
                else:
                    # 调用原类的execute方法执行任务
                    if subtask["original_problem"]!="":
                        subtask["instructions"] = subtask["original_problem"]
                    result = self.provider.execute(subtask)
                    print(result)
                
                    requester_id = self.provider.ise.requester_id
                    print("发送result给", requester_id)
                    self.provider.ise.submit_result(requester_id, result)

                # print(result)
                    # if result:
                    #     # 发送结果回请求者（原类未实现，外部补充）
                    #     self.provider.ise.send_result(sender_id, "task_result", {
                    #         "task_id": subtask.get("id"),
                    #         "result": result
                    #     })
                    #     print(f"[任务结果] 已返回给 {sender_id}")
            # except Exception as e:
            #     if self.running:  # 运行中才打印错误
            #         print(f"[任务监听错误] {str(e)}")
            time.sleep(0.5)  # 避免CPU空转

    def _wait_for_stop(self):
        """等待用户输入停止命令"""
        while self.running:
            user_input = input()
            if user_input.strip().lower() == "stop":
                self.running = False
                print("\n[Runner] 收到停止命令，正在退出...")
                # 清理资源（如关闭网络连接）
                self.provider.network.close()
                print("[Runner] 服务已停止")

if __name__ == "__main__":
    # 配置文件路径（根据实际项目调整）
    parser = argparse.ArgumentParser(description="Compute Provider Config")
    parser.add_argument("--num", default="1", type=str)
    args = parser.parse_args()
    config_path = f"./runtime/config_compute{args.num}.yaml"
    # 启动运行器
    runner = ComputeProviderRunner(config_path)
    runner.start()