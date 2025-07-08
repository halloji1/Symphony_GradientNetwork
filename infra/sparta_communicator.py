# runtime/sparta_communication.py
import os
import json
import time
import uuid
import threading
import zmq
import torch
from typing import Dict, List, Optional, Set
from protocol.lora_patch import LoRAPatch

class TopologyType:
    GLOBAL_BROADCAST = "GLOBAL_BROADCAST"
    NEIGHBOR_BROADCAST = "NEIGHBOR_BROADCAST"
    
class SpartacusCommunicator:
    """SPARTA通信机制实现，支持全域广播和邻居广播两种拓扑"""
    
    def __init__(self, node_id: str, config: Dict):
        self.node_id = node_id
        self.config = config
        self.context = zmq.Context()
        
        # 获取拓扑类型配置
        self.topology_type = TopologyType[config.get("topology_type", "GLOBAL_BROADCAST")]
        
        # 节点注册表 - 存储已知的其他节点信息
        self.node_registry = {}
        
        # 初始化通信组件
        self._init_communication_components()
        
        # 接收线程
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_callbacks = []
        self.running = False
        
        # 已处理的patch记录，避免重复处理
        self.processed_patches = set()
        
    def _init_communication_components(self):
        """初始化通信组件"""
        if self.topology_type == TopologyType.GLOBAL_BROADCAST:
            # 全域广播模式 - 使用发布-订阅模式
            self._init_global_broadcast_mode()
        elif self.topology_type == TopologyType.NEIGHBOR_BROADCAST:
            # 邻居广播模式 - 使用点对点连接
            self._init_neighbor_broadcast_mode()
    
    def _init_global_broadcast_mode(self):
        """初始化全域广播模式"""
        self.broadcast_addr = self.config.get("sparta_broadcast_addr", "tcp://*:5556")
        self.subscribe_addrs = self.config.get("sparta_subscribe_addrs", ["tcp://localhost:5556"])
        
        # 广播发送器
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(self.broadcast_addr)
        
        # 广播接收器
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        
        for addr in self.subscribe_addrs:
            self.subscriber.connect(addr)
    
    def _init_neighbor_broadcast_mode(self):
        """初始化邻居广播模式"""
        # 获取邻居节点配置
        self.neighbor_nodes = self.config.get("neighbor_nodes", {})
        
        # 创建REQ套接字连接到每个邻居
        self.req_sockets = {}
        for neighbor_id, neighbor_addr in self.neighbor_nodes.items():
            req_socket = self.context.socket(zmq.REQ)
            req_socket.connect(neighbor_addr)
            self.req_sockets[neighbor_id] = req_socket
        
        # 创建REP套接字接收来自邻居的消息
        self.rep_socket = self.context.socket(zmq.REP)
        self.rep_addr = self.config.get("neighbor_rep_addr", f"tcp://*:{5556 + hash(self.node_id) % 1000}")
        self.rep_socket.bind(self.rep_addr)
    
    def start(self):
        """启动通信器"""
        self.running = True
        self.receive_thread.start()
        print(f"[SPARTA] 通信器已启动 - {self.node_id} (拓扑: {self.topology_type.name})")
        
    def stop(self):
        """停止通信器"""
        self.running = False
        # 关闭所有套接字
        if hasattr(self, 'publisher'):
            self.publisher.close()
        if hasattr(self, 'subscriber'):
            self.subscriber.close()
        if hasattr(self, 'rep_socket'):
            self.rep_socket.close()
        for socket in getattr(self, 'req_sockets', {}).values():
            socket.close()
        self.context.term()
    
    def register_node(self, node_id: str, node_info: Dict):
        """注册新节点（主要用于邻居广播模式）"""
        if self.topology_type == TopologyType.NEIGHBOR_BROADCAST:
            if node_id not in self.neighbor_nodes and node_id != self.node_id:
                print(f"[SPARTA] 注册新邻居节点: {node_id}")
                self.neighbor_nodes[node_id] = node_info.get("addr")
                
                # 创建到新邻居的连接
                req_socket = self.context.socket(zmq.REQ)
                req_socket.connect(node_info.get("addr"))
                self.req_sockets[node_id] = req_socket
    
    def broadcast_lora_patch(self, patch: LoRAPatch):
        """根据拓扑结构广播LoRA参数变化量patch"""
        if self.topology_type == TopologyType.GLOBAL_BROADCAST:
            self._broadcast_patch_global_mode(patch)
        elif self.topology_type == TopologyType.NEIGHBOR_BROADCAST:
            self._broadcast_patch_neighbor_mode(patch)
    
    def _broadcast_patch_global_mode(self, patch: LoRAPatch):
        """在全域广播模式下广播patch"""
        patch_dict = patch.to_dict()
        
        # 构建消息
        message = {
            "sender_id": self.node_id,
            "timestamp": int(time.time()),
            "patch": patch_dict
        }
        
        # 发送消息
        self.publisher.send_json(message)
        print(f"[SPARTA] 已全域广播LoRA patch - {patch.patch_id[:6]}")
    
    def _broadcast_patch_neighbor_mode(self, patch: LoRAPatch):
        """在邻居广播模式下广播patch"""
        patch_dict = patch.to_dict()
        
        # 构建消息
        message = {
            "sender_id": self.node_id,
            "timestamp": int(time.time()),
            "patch": patch_dict
        }
        
        # 发送消息到所有邻居
        for neighbor_id, socket in self.req_sockets.items():
            try:
                socket.send_json(message)
                # 等待响应
                response = socket.recv_string()
                print(f"[SPARTA] 已向邻居 {neighbor_id} 发送LoRA patch - {patch.patch_id[:6]}")
            except Exception as e:
                print(f"[SPARTA] 向邻居 {neighbor_id} 发送消息时出错: {str(e)}")
    
    def _receive_loop(self):
        """接收消息的循环"""
        while self.running:
            try:
                if self.topology_type == TopologyType.GLOBAL_BROADCAST:
                    self._receive_global_mode()
                elif self.topology_type == TopologyType.NEIGHBOR_BROADCAST:
                    self._receive_neighbor_mode()
            except Exception as e:
                print(f"[SPARTA] 接收消息时出错: {str(e)}")
                time.sleep(1)  # 出错后等待一段时间再重试
    
    def _receive_global_mode(self):
        """在全域广播模式下接收消息"""
        # 设置超时，避免阻塞
        if self.subscriber.poll(timeout=1000) == 0:
            return
            
        message = self.subscriber.recv_json()
        self._process_received_message(message)
    
    def _receive_neighbor_mode(self):
        """在邻居广播模式下接收消息"""
        # 设置超时，避免阻塞
        if self.rep_socket.poll(timeout=1000) == 0:
            return
            
        message = self.rep_socket.recv_json()
        self._process_received_message(message)
        
        # 发送响应
        self.rep_socket.send_string("OK")
    
    def _process_received_message(self, message):
        """处理接收到的消息"""
        sender_id = message.get("sender_id")
        patch_data = message.get("patch")
        
        if not patch_data:
            return
            
        patch = LoRAPatch.from_dict(patch_data)
        
        # 避免处理自己发送的patch和已处理过的patch
        if sender_id == self.node_id or patch.patch_id in self.processed_patches:
            return
            
        self.processed_patches.add(patch.patch_id)
        
        # 调用回调函数处理接收到的patch
        for callback in self.receive_callbacks:
            callback(patch)