# Prompt Loader
import json

def load_prompts(filepath):
    """
    Load adversarial prompts from a JSON file.

    Args:
        filepath (str): Path to the prompt JSON file.

    Returns:
        list: A list of prompt dictionaries.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
