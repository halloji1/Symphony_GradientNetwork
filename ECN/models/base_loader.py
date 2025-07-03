# models/base_loader.py

from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch

class BaseModel:
    def __init__(self, model_path: str, system_prompt: str = "", device: str = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model_path = model_path
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16 if "cuda" in self.device else torch.float32)
        self.model.to(self.device)
        self.system_prompt = system_prompt.strip() + "\n" if system_prompt else ""
        self.pipeline = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer, device=0 if self.device == "cuda" else -1)

    def generate(self, user_input: str, max_new_tokens: int = 256, temperature: float = 0.7) -> str:
        prompt = self.system_prompt + user_input.strip()
        result = self.pipeline(prompt, max_new_tokens=max_new_tokens, temperature=temperature, do_sample=True, num_return_sequences=1)
        return result[0]['generated_text'][len(prompt):].strip()

    def generate_task_dag(self, user_input: str) -> dict:
        prompt = self.system_prompt + f"请将以下任务拆解为有序子任务，并以 JSON 结构输出：\n任务：{user_input}\n输出：{{\"steps\": [...], \"dependencies\": [...]}}"
        result = self.pipeline(prompt, max_new_tokens=512, temperature=0.3)[0]['generated_text']
        json_start = result.find('{')
        json_end = result.rfind('}') + 1
        try:
            structured = result[json_start:json_end]
            import json
            return json.loads(structured)
        except Exception as e:
            print(f"[Error parsing DAG output] {e}\nRaw result: {result}")
            return {"steps": [], "dependencies": []}
