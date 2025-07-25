from models.base_loader import BaseModel

prompt = f"""You are a reasoning analyzer. Given a task, determine whether it can be reliably solved in a single reasoning step by a language model without breaking it into intermediate steps.

Answer with `true` if a single-step answer is sufficient and reliable. Otherwise, answer `false`.

Task:
If $a * b = a^b + b^a$, for all positive integer values of $a$ and $b$, then what is the value of $2 * 6$?

Only output `true` or `false`.
"""

model = BaseModel("/workspace/deepseek-math-7b-instruct")
result = model.generate(prompt)
print(result)