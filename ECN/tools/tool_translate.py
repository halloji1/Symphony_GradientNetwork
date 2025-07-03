# tools/tool_translate.py

from tools.base import ToolBase

class TranslateTool(ToolBase):
    def name(self) -> str:
        return "translate"

    def description(self) -> str:
        return "将英文文本翻译为中文"

    def run(self, input_text: str) -> str:
        # 简易替代翻译示例，可替换为真实翻译 API
        sample_dict = {
            "hello": "你好",
            "world": "世界",
            "thank you": "谢谢你",
            "good morning": "早上好",
            "how are you": "你好吗"
        }
        input_lower = input_text.lower().strip()
        translation = sample_dict.get(input_lower, f"[模拟翻译] {input_text} -> 中文")
        return translation


# 示例：
if __name__ == "__main__":
    tool = TranslateTool()
    print(tool.name(), "->", tool.run("hello"))
