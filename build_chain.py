import json
import os

def prompt_chain():
    print("\n🔧 Prompt Builder - Multi-Turn Adversarial Chain")

    scenario = input("Enter scenario title: ").strip()
    category = input("Category [multi_turn]: ").strip() or "multi_turn"
    chain = []

    print("\nEnter conversation turns. Press Enter on a blank line to finish.\n")

    turn_count = 1
    while True:
        msg = input(f"Turn {turn_count}: ").strip()
        if not msg:
            break
        chain.append(msg)
        turn_count += 1

    print("\n🧠 Final Chain Preview:")
    print(f"Scenario: {scenario}")
    print(f"Category: {category}")
    for i, msg in enumerate(chain, 1):
        print(f"  Turn {i}: {msg}")

    confirm = input("\nSave this chain to prompts/multi_turn_chains.json? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Chain not saved.")
        return

    # Output file
    filepath = "prompts/multi_turn_chains.json"
    os.makedirs("prompts", exist_ok=True)

    # Load existing chains
    if os.path.isfile(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Append new chain
    data.append({
        "scenario": scenario,
        "category": category,
        "chain": chain
    })

    # Save
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("✅ Chain saved successfully!")

if __name__ == "__main__":
    prompt_chain()
