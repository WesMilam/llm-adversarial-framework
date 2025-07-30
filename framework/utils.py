import json
import os
from datetime import datetime
import google.generativeai as genai

def save_prompt(scenario, turn1, turn2, tags, topic, intent, difficulty, path="data/chained_prompts.json"):
    prompt_data = {
        "scenario": scenario,
        "turn_1": turn1,
        "turn_2": turn2,
        "tags": [tag.strip() for tag in tags if tag.strip()],
        "topic": topic,
        "intent": intent,
        "difficulty": difficulty
    }

    if os.path.exists(path):
        with open(path, "r") as f:
            existing_data = json.load(f)
    else:
        existing_data = []

    existing_data.append(prompt_data)

    with open(path, "w") as f:
        json.dump(existing_data, f, indent=4)

def load_prompts(path="data/chained_prompts.json"):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)

def log_result(prompt, response, model_name, keyword_eval, smart_eval, model_used, path="results/model_responses.csv"):
    from csv import DictWriter
    import os

    data = {
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "response": response,
        "model_name": model_name,
        "model_used": model_used,
        "keywords_flagged": keyword_eval if isinstance(keyword_eval, dict) else {},
        "smart_score": smart_eval.get("score") if isinstance(smart_eval, dict) else None,
        "intent": smart_eval.get("intent") if isinstance(smart_eval, dict) else "",
        "difficulty": smart_eval.get("difficulty") if isinstance(smart_eval, dict) else "",
        "tags": ",".join(smart_eval.get("tags", [])) if isinstance(smart_eval, dict) else ""
    }

    file_exists = os.path.isfile(path)

    with open(path, "a", newline='', encoding="utf-8") as f:
        writer = DictWriter(f, fieldnames=data.keys())
        if not file_exists:
            writer.writeheader()
        writer.writerow(data)

def generate_gemini_response(model: str, prompt: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    try:
        model_instance = genai.GenerativeModel(model)
        response = model_instance.generate_content(prompt)
        return response.text if hasattr(response, 'text') else str(response)
    except Exception as e:
        return f"Gemini Error: {e}"