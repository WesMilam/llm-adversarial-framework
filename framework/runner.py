# Runner
import os
from dotenv import load_dotenv
from framework.prompt_loader import load_prompts
import openai

# Load API keys from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def run_single_prompt(prompt):
    """
    Sends a single prompt to the GPT model and returns its response.
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
        return f"Error: {e}"

def main():
    prompts = load_prompts("prompts/prompt_injection.json")
    for idx, test in enumerate(prompts, 1):
        print(f"\n🧪 Test {idx} - Category: {test['category']}")
        print(f"Prompt: {test['prompt']}")
        response = run_single_prompt(test['prompt'])
        print(f"🧠 Model Response:\n{response}\n{'-'*60}")

if __name__ == "__main__":
    main()
