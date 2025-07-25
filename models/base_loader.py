# models/base_loader.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline, BitsAndBytesConfig
from protocol.task_contract import TaskDAG, SubTask
import torch
import re
import json
import regex

class BaseModel:
    def __init__(self, model_path: str, system_prompt: str = "", device: str = None):
        self.device = device
        self.model_path = model_path
        bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,
                llm_int8_threshold=6.0,
                llm_int8_skip_modules=None
            )
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                quantization_config=bnb_config,
                torch_dtype=torch.float16,
                device_map=self.device
            )
        # self.model.to(self.device)
        print("Running on ", device)
        self.system_prompt = system_prompt.strip() + "\n" if system_prompt else ""
        # self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device=0 if self.device == "cuda" else -1)

    def generate(self, prompt, max_new_tokens=512, temperature=0.5, top_p=0.9):
        prompt_inputs = self.tokenizer(prompt, return_tensors="pt")
        prompt_length = prompt_inputs.input_ids.shape[1]  # 获取prompt的token长度
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=True
            )
        generated_tokens = outputs[0][prompt_length:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    # def generate(self, user_input: str, max_new_tokens: int = 256, temperature: float = 0.7) -> str:
    #     prompt = self.system_prompt + user_input.strip()
    #     result = self.pipeline(prompt, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=True, num_return_sequences=1)
    #     return result[0]['generated_text'][len(prompt):].strip()

    def generate_task_dag(self, task_background: str, task_question: str, user_input: str, requirement: str) -> TaskDAG:
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
            result = raw_result.split("Output:")[1].strip()
            result = result.replace('\\', '\\\\')
            dag_dict = json.loads(result)
            steps = [SubTask(id=str(index+1), 
                                requirement=requirement, 
                                original_problem=task_question, 
                                previous_results=[task_background], 
                                instructions=s,
                                decomposed=True) for index, s in enumerate(dag_dict.get("subtasks", []))]
            if len(steps) <= 2:
                print("This task do not need decomposition")
                steps = steps = [SubTask(id=str(1),
                                requirement=requirement,
                                original_problem="",
                                previous_results=[],
                                instructions=user_input,
                                decomposed=False)]
            dependencies = []
            for step in steps:
                print(step.id, step.requirement, step.instructions)
            return TaskDAG(steps, dependencies), True
        except:
            return TaskDAG([],[]), False