import os
from dotenv import load_dotenv
from framework.prompt_loader import load_prompts
from framework.evaluator import evaluate_response
from framework.utils import get_timestamp, log_to_csv

import openai
import google.generativeai as genai

# Load API keys from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Supported models
SUPPORTED_MODELS = ["openai-gpt-4", "gemini-pro"]

def run_openai(prompt):
    """
    Send prompt to OpenAI GPT-4
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful and ethical assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"OpenAI Error: {e}"

def run_gemini(prompt):
    """
    Send prompt to Google Gemini
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

def run_model(prompt, model_name):
    """
    Dispatch prompt to selected model.
    """
    if model_name == "openai-gpt-4":
        return run_openai(prompt)
    elif model_name == "gemini-pro":
        return run_gemini(prompt)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

def main():
    # CONFIG: Choose model and prompt set
    model_name = "openai-gpt-4"  # or "gemini-pro"
    prompt_path = "prompts/prompt_injection.json"

    if model_name not in SUPPORTED_MODELS:
        raise ValueError(f"Model '{model_name}' is not supported.")

    prompts = load_prompts(prompt_path)
    timestamp = get_timestamp()
    output_file = f"results/results_{model_name}_{timestamp}.csv"
    headers = ["Test #", "Model", "Category", "Prompt", "Response", "Evaluation"]

    for idx, test in enumerate(prompts, 1):
        print(f"\n🧪 Test {idx} - [{model_name}] - Category: {test['category']}")
        print(f"Prompt: {test['prompt']}")

        response = run_model(test['prompt'], model_name)
        result = evaluate_response(test['prompt'], response)

        print(f"🧠 Model Response:\n{response}")
        print(f"✅ Evaluation Result: {result}")
        print("-" * 60)

        log_to_csv(output_file, headers, [idx, model_name, test['category'], test['prompt'], response, result])

if __name__ == "__main__":
    main()
