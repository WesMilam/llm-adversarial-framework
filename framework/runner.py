import os
import argparse
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

SUPPORTED_MODELS = ["openai-gpt-4", "gemini-pro"]

def run_openai(prompt):
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
    try:
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        response = chat.send_message(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Error: {e}"

def run_model(prompt, model_name):
    if model_name == "openai-gpt-4":
        return run_openai(prompt)
    elif model_name == "gemini-pro":
        return run_gemini(prompt)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="LLM Adversarial Testing Framework")
    parser.add_argument("--model", choices=SUPPORTED_MODELS, required=True, help="Model to use (openai-gpt-4 or gemini-pro)")
    parser.add_argument("--prompts", default="prompts/prompt_injection.json", help="Path to prompt JSON file")
    args = parser.parse_args()

    model_name = args.model
    prompt_path = args.prompts

    prompts = load_prompts(prompt_path)
    timestamp = get_timestamp()
    output_file = f"results/results_{model_name}_{timestamp}.csv"
    headers = ["Test #", "Model", "Category", "Prompt", "Response", "Evaluation"]

    # Initialize summary counters
    summary = {"PASS": 0, "FAIL": 0, "UNCLEAR": 0}

    # Run each prompt and log
    for idx, test in enumerate(prompts, 1):
        category = test.get("category", "unknown")

        print(f"\n🧪 Test {idx} - [{model_name}] - Category: {category}")
        print(f"Prompt: {test['prompt']}")

        response = run_model(test['prompt'], model_name)
        result = evaluate_response(test['prompt'], response, category)

        print(f"🧠 Model Response:\n{response}")
        print(f"✅ Evaluation Result: {result}")
        print("-" * 60)

        # Log result
        log_to_csv(output_file, headers, [idx, model_name, category, test['prompt'], response, result])

        # Update summary
        if result in summary:
            summary[result] += 1
        else:
            summary["UNCLEAR"] += 1

    # Print summary to console
    total = sum(summary.values())
    print("\n📊 Test Summary")
    print("-" * 40)
    for k, v in summary.items():
        percent = (v / total) * 100 if total > 0 else 0
        print(f"{k}: {v} ({percent:.1f}%)")
    print("-" * 40)
    print(f"Total tests run: {total}")

    # Append summary to CSV
    with open(output_file, mode="a", encoding="utf-8") as f:
        f.write("\n\nSummary,,,\n")
        for k, v in summary.items():
            f.write(f"{k},{v}\n")
        f.write(f"Total,{total}\n")

if __name__ == "__main__":
    main()
