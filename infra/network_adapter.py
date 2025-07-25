import socket
import json
import threading
from typing import Dict, Callable, List, Optional, Tuple
from dataclasses import asdict
import time

class NetworkAdapter:
    def __init__(self, node_id: str, config: dict):
        self.node_id = node_id
        self.host = config["network"]["host"]
        self.port = config["network"]["port"]
        self.neighbors: Dict[str, Tuple[str, int]] = {}  # 节点ID → (主机, 端口)
        self.handlers: Dict[str, Callable] = {}
        self.server_socket = None
        self.receive_thread = None
        self._start_server()  # 启动接收线程

    def register_handler(self, msg_type: str, handler: Callable):
        """注册消息处理器"""
        self.handlers[msg_type] = handler

    def add_neighbor(self, node_id: str, host: str, port: int):
        """添加邻居节点"""
        self.neighbors[node_id] = (host, port)

    def send(self, target_id: str, msg_type: str, data) -> bool:
        """
        向目标节点发送消息
        
        Args:
            target_id: 目标节点ID
            msg_type: 消息类型（如"beacon", "task_contract"）
            data: 要发送的数据对象（需支持JSON序列化）
            
        Returns:
            发送成功返回True，失败返回False
        """
        if target_id not in self.neighbors:
            print(f"错误: 未知节点ID {target_id}")
            return False
            
        host, port = self.neighbors[target_id]
        
        try:
            # 构建消息包
            message = {
                "sender_id": self.node_id,
                "target_id": target_id,
                "msg_type": msg_type,
                "data": data.to_dict(),
                "timestamp": time.time()
            }
            
            # 创建TCP连接并发送消息
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5)  # 设置超时时间5秒
                s.connect((host, port))
                
                # 将消息转换为JSON并编码为字节
                msg_json = json.dumps(message)
                msg_bytes = msg_json.encode('utf-8')
                
                # 发送消息长度前缀（4字节整数）
                s.sendall(len(msg_bytes).to_bytes(4, 'big'))
                # 发送消息内容
                s.sendall(msg_bytes)
                
                # 接收响应（可选）
                response = self._receive_response(s)
                return response.get("status") == "success"
                
        except (socket.error, json.JSONDecodeError) as e:
            print(f"发送消息失败 ({target_id}): {e}")
            return False

    def broadcast(self, msg_type: str, data, exclude: List[str] = None):
        """向所有邻居广播消息（可排除指定节点）"""
        exclude = exclude or []
        for neighbor_id in list(self.neighbors.keys()):
            if neighbor_id not in exclude:
                self.send(neighbor_id, msg_type, data)

    def _start_server(self):
        """启动服务器线程接收消息"""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        
        self.receive_thread = threading.Thread(target=self._receive_loop, daemon=True)
        self.receive_thread.start()
        print(f"节点 {self.node_id} 网络适配器已启动，监听 {self.host}:{self.port}")

    def _receive_loop(self):
        """消息接收循环"""
        while True:
            try:
                conn, addr = self.server_socket.accept()
                with conn:
                    # 接收消息长度前缀
                    len_bytes = conn.recv(4)
                    if not len_bytes:
                        continue
                        
                    msg_length = int.from_bytes(len_bytes, 'big')
                    
                    # 接收完整消息
                    msg_bytes = b""
                    while len(msg_bytes) < msg_length:
                        chunk = conn.recv(min(4096, msg_length - len(msg_bytes)))
                        if not chunk:
                            break
                        msg_bytes += chunk
                        
                    if len(msg_bytes) != msg_length:
                        continue
                        
                    # 解析消息
                    msg_json = msg_bytes.decode('utf-8')
                    message = json.loads(msg_json)
                    
                    # 调用对应的消息处理器
                    self._handle_message(message)
                    
            except Exception as e:
                print(f"接收消息出错: {e}")

    def _handle_message(self, message):
        """处理接收到的消息"""
        msg_type = message.get("msg_type")
        sender_id = message.get("sender_id")
        data = message.get("data")

        if not msg_type or not sender_id or data is None:
            print(f"无效消息格式: {message}")
            return
            
        if msg_type in self.handlers:
            # 反序列化数据
            deserialized_data = self._deserialize_data(data)
            self.handlers[msg_type](sender_id, deserialized_data)
        else:
            print(f"未知消息类型: {msg_type}")

    def _receive_response(self, socket_obj) -> Dict:
        """接收并解析响应消息"""
        try:
            # 接收响应长度前缀
            len_bytes = socket_obj.recv(4)
            if not len_bytes:
                return {"status": "error", "message": "没有响应"}
                
            resp_length = int.from_bytes(len_bytes, 'big')
            
            # 接收完整响应
            resp_bytes = b""
            while len(resp_bytes) < resp_length:
                chunk = socket_obj.recv(min(4096, resp_length - len(resp_bytes)))
                if not chunk:
                    break
                resp_bytes += chunk
                
            if len(resp_bytes) != resp_length:
                return {"status": "error", "message": "响应不完整"}
                
            # 解析响应
            resp_json = resp_bytes.decode('utf-8')
            return json.loads(resp_json)
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _serialize_data(self, data):
        """序列化数据（支持dataclass）"""
        if hasattr(data, "__dict__"):  # 处理类实例
            return asdict(data)
        return data

    def _deserialize_data(self, data):
        """反序列化数据"""
        return data  # 简化实现，实际应根据数据类型进行反序列化