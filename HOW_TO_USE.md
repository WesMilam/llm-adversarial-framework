# 🧩 How to Use This Framework

This document explains how to configure and use the LLM Adversarial Testing Framework with your own credentials and workflow.

---

## 🔑 Step 1: Get API Access

### ✅ OpenAI (GPT-4, GPT-4o)
1. Visit: https://platform.openai.com/account/api-keys
2. Create a new API key.
3. **Add it to your `.env` file** like this:

```ini
OPENAI_API_KEY=your_api_key_here
```

Note: This is separate from ChatGPT Plus.

---

### ✅ Gemini (Google AI Studio)
1. Visit: https://makersuite.google.com/app/apikey
2. Generate a Gemini API key.
3. Add this to `.env` as:

```ini
GEMINI_API_KEY=your_api_key_here
```

---

## 📁 Step 2: Create Required Folders (if missing)

Make sure the following folders exist:
- `data/` – for prompt sets
- `results/` – for logged output

These will auto-generate if missing, but can also be created manually.

---

## 💡 Step 3: Run the App

Use the terminal:
```bash
streamlit run chain_tool_gui_openai_v2.py
```

Then open the browser to:
```
http://localhost:8501
```

---

## 🧠 Step 4: Create & Test Prompts

1. Go to the **Prompt Builder** tab.
2. Define a 2-turn adversarial conversation.
3. Assign tags, topic, intent, and difficulty.
4. Click **Save Prompt**.

Then visit the **Test** tab to:
- Choose your model (GPT or Gemini)
- Filter by topic, difficulty, or intent
- Run and log results

---

## 📊 Where Results Are Logged

- Prompt text: `data/chained_prompts.json`
- Model output logs: `results/model_responses.csv`

Use Power BI, pandas, or Excel to analyze trends.

---

For any issue, feel free to explore each module in `framework/`.