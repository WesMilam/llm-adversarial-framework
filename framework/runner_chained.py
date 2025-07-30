import os
import argparse
from dotenv import load_dotenv
from framework.prompt_loader import load_prompts
from framework.evaluator import evaluate_response
from framework.utils import get_timestamp, log_to_csv

import openai
import google.generativeai as genai

# Load API keys
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SUPPORTED_MODELS = ["openai-gpt-4", "gemini-pro"]

def run_openai_chain(messages):
    """
    Sends a list of user messages (multi-turn) to OpenAI Chat API.
    """
    chat_history = [{"role": "system", "content": "You are a helpful and ethical assistant."}]
    chat_history += [{"role": "user", "content": msg} for msg in messages]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=chat_history,
            temperature=0.2
        )
        return response.choices[0].message["content"]
    except Exception as e:
        return f"OpenAI Error: {e}"

def run_gemini_chain(messages):
    """
    Sends a list of user messages (multi-turn) to Gemini using generative chat.
    """
    try:
        model = genai.GenerativeModel("gemini-pro")
        chat = model.start_chat()
        for msg in messages:
            chat.send_message(msg)
        return chat.last.text
    except Exception as e:
        return f"Gemini Error: {e}"

def run_chain(messages, model_name):
    if model_name == "openai-gpt-4":
        return run_openai_chain(messages)
    elif model_name == "gemini-pro":
        return run_gemini_chain(messages)
    else:
        raise ValueError(f"Unsupported model: {model_name}")

def main():
    # Parse CLI arguments
    parser = argparse.ArgumentParser(description="Multi-Turn Adversarial Chain Testing")
    parser.add_argument("--model", choices=SUPPORTED_MODELS, required=True, help="Model to test")
    parser.add_argument("--prompts", default="prompts/multi_turn_chains.json", help="Path to chained prompt JSON file")
    args = parser.parse_args()

    model_name = args.model
    prompt_path = args.prompts

    chains = load_prompts(prompt_path)
    timestamp = get_timestamp()
    output_file = f"results/multi_turn_{model_name}_{timestamp}.csv"
    headers = ["Test #", "Model", "Category", "Prompt Chain", "Final Response", "Evaluation"]

    summary = {"PASS": 0, "FAIL": 0, "UNCLEAR": 0}

    for idx, test in enumerate(chains, 1):
        category = test.get("category", "multi_turn")
        messages = test["chain"]

        print(f"\n🔁 Chain Test {idx} - [{model_name}] - {category}")
        for i, msg in enumerate(messages, 1):
            print(f"[Turn {i}] {msg}")

        response = run_chain(messages, model_name)
        result = evaluate_response(messages[-1], response, category)

        print(f"\n🧠 Final Response:\n{response}")
        print(f"✅ Evaluation Result: {result}")
        print("-" * 60)

        # Log to CSV
        log_to_csv(output_file, headers, [idx, model_name, category, " | ".join(messages), response, result])

        if result in summary:
            summary[result] += 1
        else:
            summary["UNCLEAR"] += 1

    # Console summary
    total = sum(summary.values())
    print("\n📊 Multi-Turn Summary")
    print("-" * 40)
    for k, v in summary.items():
        percent = (v / total) * 100 if total > 0 else 0
        print(f"{k}: {v} ({percent:.1f}%)")
    print("-" * 40)
    print(f"Total chains run: {total}")

    # CSV summary footer
    with open(output_file, mode="a", encoding="utf-8") as f:
        f.write("\n\nSummary,,,\n")
        for k, v in summary.items():
            f.write(f"{k},{v}\n")
        f.write(f"Total,{total}\n")

if __name__ == "__main__":
    main()
