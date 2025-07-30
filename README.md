# 🧠 LLM Adversarial Testing Framework

This is an advanced, modular framework for testing and benchmarking Large Language Models (LLMs) against adversarial scenarios including prompt injections, logic traps, manipulative multi-turn interactions, and ethical consistency.

## 🔧 Features

- ✅ Support for **OpenAI GPT-4, GPT-4o, GPT-3.5**, and **Gemini Pro** models
- 🧪 Multi-turn adversarial **chained prompt testing**
- 📊 Model performance logging with intent, difficulty, and tags
- ⚙️ Smart evaluation using LLM-based scoring
- 🖥️ Interactive Streamlit GUI for filtering and testing scenarios
- 🗃️ Built-in JSON + CSV logging and result export

## 📁 Project Structure

```
llm-adversarial-framework/
│
├── chain_tool_gui_openai_v2.py        # Final merged GUI
├── .env                               # Store your API keys here
│
├── framework/
│   ├── runner.py                      # Main test runner
│   ├── runner_chained.py             # Multi-turn chaining
│   ├── evaluator.py                  # Evaluation logic
│   ├── evaluation_utils_openai_v1.py # OpenAI scoring helpers
│   ├── utils.py                      # Prompt save/load, Gemini, logging
│   └── __init__.py
│
├── data/
│   └── chained_prompts.json          # Saved user prompts
│
├── results/
│   └── model_responses.csv           # Logs test results
│
└── README.md
    HOW_TO_USE.md
```

## 🚀 Quick Start

```bash
conda create -n llm-adversarial-framework python=3.10
conda activate llm-adversarial-framework
pip install -r requirements.txt
streamlit run chain_tool_gui_openai_v2.py
```

## 🔐 Environment Setup

Create a `.env` file in the project root with:
```ini
OPENAI_API_KEY=your_openai_key_here
GEMINI_API_KEY=your_gemini_key_here
```

