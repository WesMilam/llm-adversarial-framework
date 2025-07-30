import json

PROMPT_FILE = "prompts/multi_turn_chains.json"

def is_valid_prompt(entry):
    return all([
        isinstance(entry.get("scenario"), str) and entry["scenario"].strip(),
        isinstance(entry.get("topic"), str) and entry["topic"].strip(),
        isinstance(entry.get("tags"), list),
        isinstance(entry.get("chain"), list) and len(entry["chain"]) > 0
    ])

def lint_prompts(remove_invalid=False):
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    valid = []
    invalid = []

    for p in prompts:
        if is_valid_prompt(p):
            valid.append(p)
        else:
            invalid.append(p)

    print(f"✅ Valid entries: {len(valid)}")
    print(f"❌ Invalid entries: {len(invalid)}")

    if invalid:
        print("\n--- Invalid Entries ---")
        for i, bad in enumerate(invalid, 1):
            print(f"[{i}] {json.dumps(bad, indent=2)}")

    if remove_invalid and invalid:
        with open(PROMPT_FILE, "w", encoding="utf-8") as f:
            json.dump(valid, f, indent=2)
        print("\n🧹 Removed invalid entries and saved cleaned file.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--remove", action="store_true", help="Remove invalid entries")
    args = parser.parse_args()

    lint_prompts(remove_invalid=args.remove)