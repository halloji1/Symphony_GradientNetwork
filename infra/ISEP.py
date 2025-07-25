# ISEP.py
from typing import Dict, List, Optional
from uuid import uuid4
import time
from threading import Timer
from queue import Queue
from protocol.beacon import Beacon
from protocol.response import BeaconResponse
from protocol.task_contract import TaskContract, TaskResult
from protocol.task_contract import TaskDAG, SubTask
from infra.network_adapter import NetworkAdapter

class ISEPClient:
    """简化版ISEP协议，适配TaskRequester的调用方式"""
    
    def __init__(self, node_id: str, network_adapter: NetworkAdapter, response_timeout: int = 1):
        self.node_id = node_id
        self.network = network_adapter
        self.response_timeout = response_timeout
        self.pending_tasks: Dict[str, List[BeaconResponse]] = {}  # task_id -> responses
        self.beacon_queue = Queue()  # 新增：用于存储接收到的Beacon消息
        self.subtask_queue = Queue()
        self.task_result_queue = Queue()
        self.task_allocation = {}
        self.requester_id = ""
        
        # 注册消息处理器
        self.network.register_handler("beacon", self._handle_beacon)
        self.network.register_handler("beacon_response", self._handle_beacon_response)
        self.network.register_handler("task_allocation", self._handle_task_allocation)
        self.network.register_handler("task_contract", self._handle_task)
        self.network.register_handler("task_result", self._handle_task_result)
    
    def broadcast_and_collect(self, beacon: Beacon) -> List[BeaconResponse]:
        """广播Beacon并收集响应"""
        self.pending_tasks[beacon.task_id] = []
        
        # 广播Beacon消息
        self.network.broadcast("beacon", beacon)
        
        # # 启动超时定时器（实际使用中可能需要更复杂的异步处理）
        # Timer(self.response_timeout, self._timeout_collect, args=[beacon.task_id]).start()

        candidates = [] # 各个compute provider的id和能力得分

        time.sleep(self.response_timeout)
        responses = self.pending_tasks[beacon.task_id]
        for response in responses:
            candidates.append((response["responder_id"], response["match_score"]))
                    
        # 简化实现：立即返回空列表，实际响应通过回调收集
        return candidates
    
    def send_response(self, target_id, msg_type, response):
        self.network.send(target_id, msg_type, response)
    
    def delegate_task(self, executor_id: str, subtask: SubTask) -> str:
        """委派子任务给执行者"""
        contract = TaskContract(
            task_id=subtask.id,
            assigned_to=executor_id,
            original_problem=subtask.original_problem,
            previous_results=subtask.previous_results,
            instructions=subtask.instructions,
            decomposed=subtask.decomposed
        )
        
        # 发送任务合同
        self.network.send(executor_id, "task_contract", contract)
    
    def submit_result(self, target_id, result):
        """提交任务结果"""
        # 查找任务ID（实际实现需要维护合同ID到任务ID的映射）
        
        result = TaskResult(
            target_id=target_id,
            executer_id=self.node_id,
            result=result
        )
        
        # 发送结果（需要知道任务分配者的ID）
        self.network.send(target_id, "task_result", result)
    
    def _handle_beacon(self, sender_id: str, beacon: Beacon):
        """处理接收到的Beacon消息"""
        # # 转发给其他节点（简化：直接转发）
        # self.network.broadcast("beacon", beacon, exclude=[sender_id])
        # 新增：将接收到的Beacon消息放入队列
        self.beacon_queue.put((sender_id, "beacon", beacon))
    
    def _handle_beacon_response(self, sender_id: str, response: BeaconResponse):
        """处理接收到的Beacon响应"""
        self.pending_tasks[response["task_id"]].append(response)

    def _handle_task_allocation(self, requester_id: str, task_allocation):
        """处理接收到的Task Allocation消息"""
        print("receive task allocation frm ", requester_id)
        self.requester_id = requester_id
        self.task_allocation = task_allocation

    def _handle_task(self, sender_id: str, task: TaskContract):
        """处理接收到的Beacon消息"""
        # 新增：将接收到的task消息放入队列
        self.subtask_queue.put((sender_id, "subtask", task))
    
    def _handle_task_result(self, sender_id: str, result: TaskResult):
        """处理接收到的任务结果"""
        # 可以添加回调机制通知TaskRequester
        print("result", result)
        self.task_result_queue.put((sender_id, "task_result", result))
    
    def _timeout_collect(self, task_id: str):
        """超时处理，停止收集响应"""
        if task_id in self.pending_tasks:
            # 这里可以触发回调通知TaskRequester响应收集完成
            print(f"任务 {task_id} 的响应收集已完成")
            # self.pending_tasks.pop(task_id)  # 实际应在TaskRequester读取后删除

    def receive_beacon(self, timeout=None):
        """从队列中获取接收到的Beacon消息"""
        try:
            return self.beacon_queue.get(timeout=timeout)
        except Exception:
            return None, None, None

    def receive_task(self, timeout=None):
        """从队列中获取接收到的task消息"""
        try:
            return self.subtask_queue.get(timeout=timeout)
        except Exception:
            return None, None, None
        
    def receive_result(self, timeout=None):
        """从队列中获取接收到的result消息"""
        try:
            return self.task_result_queue.get(timeout=timeout)
        except Exception:
            return None, None, None