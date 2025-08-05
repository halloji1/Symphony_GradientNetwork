# models/base_loader.py

import json
import regex
from typing import Dict, Any, List, Tuple
from vllm import LLM, SamplingParams
import subprocess

class BaseModel:
    def __init__(self, model_path: str, system_prompt: str = "", device: str = None):
        self.device = device
        self.model_path = model_path
        
        self.llm = LLM(model=model_path)
        print("Running on ", device)
        self.system_prompt = system_prompt.strip() + "\n" if system_prompt else ""
        

    def generate(self, prompt, max_new_tokens=512, temperature=0.5, top_p=0.9):
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_new_tokens,
        )
        outputs = self.llm.generate(prompt, sampling_params)
        return outputs[0].outputs[0].text.strip()


    def generate_task_dag(self, task_background: str, task_question: str, user_input: str, requirement: str) -> List:
        prompt = f"""
You are a problem decomposer, not a solver. Your task is to break down a complex math or logic problem into a sequence of strictly computable sub-questions. Each sub-question must represent a well-defined, executable step toward solving the original problem.

Each subtask must be phrased as a question. Do not solve the problem or output the final answer.

You MUST strictly output the result in the following **valid JSON** format:

Output:
{{
"original_question": "<repeat the original question>",
"subtasks": [
    "Q1: ...",
    "Q2: ...",
    ...
]
}}

⚠️ Important Rules:

- Do NOT include any final answer, intermediate answer, or numerical result.
- Do NOT perform or explain any computation.
- Do NOT include any text outside the JSON object.
- Each subtask must be directly computable (e.g., calculate a value, rewrite an expression, identify a condition).
- Use clear and concise language appropriate for step-by-step problem solving.

Here are some examples:

Example 1:
Input:
One root of the equation $5x^2+kx=4$ is 2. What is the other?

Output:
{{
  "original_question": "One root of the equation $5x^2+kx=4$ is 2. What is the other?",
  "subtasks": [
    "Q1: What is the equation rewritten in standard quadratic form?",
    "Q2: What is the product of the roots of this quadratic equation?",
    "Q3: Given one root is 2, what is the other root?"
  ]
}}

Example 2:
Input:
A box contains 3 red and 5 blue balls. Two balls are drawn without replacement. What is the probability that both are red?

Output:
{{
  "original_question": "A box contains 3 red and 5 blue balls. Two balls are drawn without replacement. What is the probability that both are red?",
  "subtasks": [
    "Q1: How many total balls are in the box?",
    "Q2: What is the probability that the first ball drawn is red?",
    "Q3: What is the probability that the second ball drawn is red given that the first was red?",
    "Q4: What is the product of the two probabilities?"
  ]
}}

Do NOT include any explanation, prefix, or suffix before or after the JSON. Output ONLY the JSON object.

Now decompose the following problem:

Input:
{user_input}
"""

        raw_result = self.generate(prompt, max_new_tokens=512, temperature=0.25)
        try:
            match = re.search(r'\{[^{}]*\}', raw_result, re.DOTALL)
            result = match.group(0)
            proc = subprocess.run(
                      ["node", "repair.js"],
                      input=result.encode("utf-8"),
                      stdout=subprocess.PIPE,
                      stderr=subprocess.PIPE,)
            repaired = proc.stdout.decode("utf-8")
            dag_dict = json.loads(repaired)
            steps = {}
            for index, s in enumerate(dag_dict.get("subtasks", [])):
                steps[str(index+1)] = [s, requirement]

            for subtask_id in steps:
                print(steps[subtask_id])

            return steps, True
        except:
            return {}, False
    

    def extract_task(self, user_input):
        prompt = f"""You are a text extractor. Your task is ONLY to separate the background information from the question in math problem statements.

Each input contains:
- Background: context, assumptions, formulas, constraints, and setup.
- Question: the final sentence or phrase that asks what needs to be found, calculated, or determined.

⚠️ IMPORTANT RULES:
- DO NOT solve or explain anything.
- DO NOT rewrite or infer any missing values.
- DO NOT modify, simplify, or expand any math expressions.
- DO NOT perform any calculations.
- DO NOT guess or assume anything.
- Only CUT the question part from the background and return both.

If the question comes after a comma, move everything after that comma to the "question".

Return your output in the following strict JSON format:
{{
  "background": "<only the setup or context>",
  "question": "<only the question sentence>"
}}

---

Example:

Input:
The perimeter of a rectangle is 24 inches. What is the number of square inches in the maximum possible area for this rectangle?

Output:
{{
  "background": "The perimeter of a rectangle is 24 inches.",
  "question": "What is the number of square inches in the maximum possible area for this rectangle?"
}}

---

Input:
If $A=2+i$, $O=-4$, $P=-i$, and $S=2+4i$, find $A-O+P+S$.

Output:
{{
  "background": "If $A=2+i$, $O=-4$, $P=-i$, and $S=2+4i$.",
  "question": "Find $A-O+P+S$"
}}

---

Now extract background and question from the following input.
Remember: do NOT solve the problem. Only extract.

Input:
{user_input}
"""

        result = self.generate(prompt)
        try:
            match = re.search(r'\{[^{}]*\}', result, re.DOTALL)
            json_str = match.group(0)
            proc = subprocess.run(
                        ["node", "repair.js"],
                        input=json_str.encode("utf-8"),
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,)
            repaired = proc.stdout.decode("utf-8")
            data = json.loads(repaired)
            return data["background"], data["question"], True
        except:
            return "", "", False
