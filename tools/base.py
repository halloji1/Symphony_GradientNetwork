# tools/base.py

from abc import ABC, abstractmethod

class ToolBase(ABC):
    @abstractmethod
    def name(self) -> str:
        """工具名称"""
        pass

    @abstractmethod
    def description(self) -> str:
        """工具功能简述"""
        pass

    @abstractmethod
    def run(self, input_text: str) -> str:
        """执行工具主功能"""
        pass
