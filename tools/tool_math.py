# tools/tool_math.py

from tools.base import ToolBase

class MathTool(ToolBase):
    def name(self) -> str:
        return "math"

    def description(self) -> str:
        return "执行简单的数学表达式求值（仅限加减乘除）"

    def run(self, input_text: str) -> str:
        try:
            expression = input_text.strip()
            # 安全地求值（禁用内置函数）
            result = eval(expression, {"__builtins__": None}, {})
            return f"结果：{result}"
        except Exception as e:
            return f"[错误] 无法解析表达式：{e}"

# 示例：
if __name__ == "__main__":
    tool = MathTool()
    print(tool.name(), "->", tool.run("2 + 3 * 4"))
