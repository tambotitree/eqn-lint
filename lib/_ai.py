# lib/_ai.py
import os, json
from ._budget import RateLimiter

class AIClient:
    def __init__(self, model, rate=0.5, max_tokens=1200):
        self.model = model
        self.rate = RateLimiter(rate)
        self.max_tokens = max_tokens

    def complete(self, system, user, fewshot=None):
        self.rate.wait()
        # Dispatch selector
        if self.model.startswith("ollama:"):
            return self._ollama(system, user, fewshot)
        else:
            return self._openai(system, user, fewshot)

    def _openai(self, system, user, fewshot):
        import openai
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        msgs = [{"role":"system","content":system}]
        if fewshot:
            msgs += fewshot
        msgs.append({"role":"user","content":user})
        resp = client.chat.completions.create(
            model=self.model,
            messages=msgs,
            temperature=0,
            max_tokens=self.max_tokens
        )
        return resp.choices[0].message.content

    def _ollama(self, system, user, fewshot):
        import requests
        model = self.model.split(":",1)[1]
        prompt = f"[SYSTEM]\n{system}\n\n[CONTEXT]\n{(fewshot or '')}\n\n[USER]\n{user}"
        r = requests.post("http://localhost:11434/api/generate",
                          json={"model": model, "prompt": prompt, "options":{"num_predict": self.max_tokens}})
        r.raise_for_status()
        out=[]
        for line in r.iter_lines(decode_unicode=True):
            if not line: continue
            out.append(json.loads(line)["response"])
        return "".join(out)