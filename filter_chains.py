import json
import argparse
import os

def load_chains(filepath):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return []

    with open(filepath, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            print("❌ Invalid JSON format.")
            return []

def filter_chains(chains, tags=None, topics=None):
    def match(entry, field, values):
        entry_values = entry.get(field, [])
        return any(val in entry_values for val in values)

    filtered = []
    for chain in chains:
        tag_match = match(chain, "tags", tags) if tags else True
        topic_match = match(chain, "topics", topics) if topics else True
        if tag_match and topic_match:
            filtered.append(chain)
    return filtered

def save_filtered_chains(chains, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chains, f, indent=2)
    print(f"✅ Filtered chains saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Filter multi-turn chains by tag or topic")
    parser.add_argument("--input", default="prompts/multi_turn_chains.json", help="Path to input JSON file")
    parser.add_argument("--output", default="prompts/filtered_chains.json", help="Path to save filtered output")
    parser.add_argument("--tags", help="Comma-separated tags to filter by")
    parser.add_argument("--topics", help="Comma-separated topics to filter by")
    args = parser.parse_args()

    tags = [t.strip() for t in args.tags.split(",")] if args.tags else None
    topics = [t.strip() for t in args.topics.split(",")] if args.topics else None

    chains = load_chains(args.input)
    if not chains:
        return

    filtered = filter_chains(chains, tags, topics)
    if not filtered:
        print("⚠️ No chains matched the filter criteria.")
        return

    save_filtered_chains(filtered, args.output)

if __name__ == "__main__":
    main()
