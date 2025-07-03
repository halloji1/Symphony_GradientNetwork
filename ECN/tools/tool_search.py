# tools/tool_search.py

from tools.base import ToolBase
import random

class SearchTool(ToolBase):
    def name(self) -> str:
        return "search"

    def description(self) -> str:
        return "模拟搜索引擎返回摘要结果"

    def run(self, input_text: str) -> str:
        # 假设搜索结果由关键词生成摘要片段
        fake_snippets = [
            f"{input_text} 是一种常见的主题，在多个来源中被提及。",
            f"根据最近的研究，{input_text} 涉及多个重要方面...",
            f"以下是关于 '{input_text}' 的搜索摘要：\n- 来源 A：...\n- 来源 B：...",
            f"{input_text} 的定义和背景可参见百科、论坛等资料。",
        ]
        return random.choice(fake_snippets)


# 示例：
if __name__ == "__main__":
    tool = SearchTool()
    print(tool.name(), "->", tool.run("quantum computing"))
