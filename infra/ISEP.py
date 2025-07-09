from typing import Dict, List, Optional
from uuid import uuid4
import time
from threading import Timer

from protocol.beacon import Beacon
from protocol.response import BeaconResponse
from protocol.task_contract import TaskContract, TaskResult
from protocol.task_contract import TaskDAG, SubTask
from infra.network_adapter import NetworkAdapter

class ISEPClient:
    """简化版ISEP协议，适配TaskRequester的调用方式"""
    
    def __init__(self, node_id: str, network_adapter: NetworkAdapter, response_timeout: int = 10):
        self.node_id = node_id
        self.network = network_adapter
        self.response_timeout = response_timeout
        self.pending_tasks: Dict[str, List[BeaconResponse]] = {}  # task_id -> responses
        
        # 注册消息处理器
        self.network.register_handler("beacon", self._handle_beacon)
        self.network.register_handler("beacon_response", self._handle_beacon_response)
        self.network.register_handler("task_result", self._handle_task_result)
    
    def broadcast_and_collect(self, beacon: Beacon) -> List[BeaconResponse]:
        """广播Beacon并收集响应"""
        self.pending_tasks[beacon.task_id] = []
        
        # 广播Beacon消息
        self.network.broadcast("beacon", beacon)
        
        # 启动超时定时器（实际使用中可能需要更复杂的异步处理）
        Timer(self.response_timeout, self._timeout_collect, args=[beacon.task_id]).start()

        candidates = [] # 各个compute provider的id和能力得分

        time.sleep(self.response_timeout)
        responses = self.pending_tasks[beacon.task_id]
        for response in responses:
            candidates.append((response.responder_id, response.match_score))
                    
        # 简化实现：立即返回空列表，实际响应通过回调收集
        return candidates
    
    def send_response(self, target_id, msg_type, response):
        self.network.send(target_id, msg_type, response)
    
    def delegate_task(self, executor_id: str, subtask: SubTask) -> str:
        """委派子任务给执行者"""
        contract_id = str(uuid4())
        contract = TaskContract(
            contract_id=contract_id,
            task_id=subtask.id,
            assignee_id=executor_id,
            input_data=subtask.input_data,
            instructions=subtask.instructions,
            deadline=time.time() + 3600  # 默认1小时截止
        )
        
        # 发送任务合同
        self.network.send(executor_id, "task_contract", contract)
        return contract_id
    
    def submit_result(self, contract_id: str, output_data: dict, status: str = "success"):
        """提交任务结果"""
        # 查找任务ID（实际实现需要维护合同ID到任务ID的映射）
        task_id = contract_id  # 简化示例，实际需要映射
        
        result = TaskResult(
            contract_id=contract_id,
            output_data=output_data,
            status=status
        )
        
        # 发送结果（需要知道任务分配者的ID）
        self.network.send("task_allocator_id", "task_result", result)
    
    def _handle_beacon(self, sender_id: str, beacon: Beacon):
        """处理接收到的Beacon消息"""
        # 转发给其他节点（简化：直接转发）
        self.network.broadcast("beacon", beacon, exclude=[sender_id])
    
    def _handle_beacon_response(self, sender_id: str, response: BeaconResponse):
        """处理接收到的Beacon响应"""
        if response.task_id in self.pending_tasks:
            self.pending_tasks[response.task_id].append(response)
    
    def _handle_task_result(self, sender_id: str, result: TaskResult):
        """处理接收到的任务结果"""
        # 可以添加回调机制通知TaskRequester
        print(f"收到任务结果: {result.contract_id}, 状态: {result.status}")
    
    def _timeout_collect(self, task_id: str):
        """超时处理，停止收集响应"""
        if task_id in self.pending_tasks:
            # 这里可以触发回调通知TaskRequester响应收集完成
            print(f"任务 {task_id} 的响应收集已完成")
            # self.pending_tasks.pop(task_id)  # 实际应在TaskRequester读取后删除