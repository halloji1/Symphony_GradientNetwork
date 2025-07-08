import os
import json
import time
import uuid
import threading
import zmq
import torch
from typing import Dict, List, Optional
from protocol.lora_patch import LoRAPatch

class SpartacusCommunicator:  
    def __init__(self, node_id: str, config: Dict):
        self.node_id = node_id
        self.config = config
        self.context = zmq.Context()
        
        # 广播地址和端口
        self.broadcast_addr = config.get("sparta_broadcast_addr", "tcp://*:5556")
        self.subscribe_addr = config.get("sparta_subscribe_addr", "tcp://localhost:5556")
        
        # 广播发送器
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(self.broadcast_addr)
        
        # 广播接收器
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect(self.subscribe_addr)
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")  # 订阅所有消息
        
        # 接收线程
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_callbacks = []
        self.running = False
        
        # 已处理的patch记录，避免重复处理
        self.processed_patches = set()
        
    def start(self):
        """启动通信器"""
        self.running = True
        self.receive_thread.start()
        print(f"[SPARTA] 通信器已启动 - {self.node_id}")
        
    def stop(self):
        """停止通信器"""
        self.running = False
        self.publisher.close()
        self.subscriber.close()
        self.context.term()
        
    def register_callback(self, callback):
        """注册接收到消息时的回调函数"""
        self.receive_callbacks.append(callback)
        
    def broadcast_lora_patch(self, patch: LoRAPatch):
        """广播LoRA参数变化量patch"""
        patch_dict = patch.to_dict()
        
        # 构建消息
        message = {
            "sender_id": self.node_id,
            "timestamp": int(time.time()),
            "patch": patch_dict
        }
        
        # 发送消息
        self.publisher.send_json(message)
        print(f"[SPARTA] 已广播LoRA patch - {patch.patch_id[:6]}")
        
    def _receive_loop(self):
        """接收消息的循环"""
        while self.running:
            try:
                # 设置超时，避免阻塞
                if self.subscriber.poll(timeout=1000) == 0:
                    continue
                    
                message = self.subscriber.recv_json()
                sender_id = message.get("sender_id")
                patch_data = message.get("patch")
                
                if not patch_data:
                    continue
                    
                patch = LoRAPatch.from_dict(patch_data)
                
                # 避免处理自己发送的patch和已处理过的patch
                if sender_id == self.node_id or patch.patch_id in self.processed_patches:
                    continue
                    
                self.processed_patches.add(patch.patch_id)
                
                # 调用回调函数处理接收到的patch
                for callback in self.receive_callbacks:
                    callback(patch)
                    
            except Exception as e:
                print(f"[SPARTA] 接收消息时出错: {str(e)}")
                time.sleep(1)  # 出错后等待一段时间再重试