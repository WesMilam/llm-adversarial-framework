# Final GUI with topic filter dropdown fix applied
import streamlit as st
import json
import os
import openai
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
from framework.gemini_model_utils import setup_gemini, call_gemini
from framework.response_logging_utils import log_response
from framework.evaluation_utils import evaluate_response, llm_self_evaluate

PROMPT_FILE = "prompts/multi_turn_chains.json"
RESULTS_FILE = "results/model_responses.csv"

def load_chains():
    if not os.path.exists(PROMPT_FILE):
        return []
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chains(chains):
    os.makedirs("prompts", exist_ok=True)
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        json.dump(chains, f, indent=2)

def load_results():
    import pandas as pd
    if not os.path.exists(RESULTS_FILE):
        return pd.DataFrame()
    return pd.read_csv(RESULTS_FILE)

def prompt_builder_ui():
    st.subheader("🧱 Build New Prompt Chain")
    scenario = st.text_input("Scenario Name")
    turns = []
    for i in range(1, 6):
        turn = st.text_input(f"Turn {i}", key=f"turn_{i}")
        if turn:
            turns.append(turn)
    topic = st.text_input("Topic")
    tags = st.text_input("Tags (comma-separated)")
    intent = st.selectbox("Intent", ["harmless", "manipulative", "coercive", "deceptive"])
    difficulty = st.selectbox("Difficulty", ["easy", "moderate", "hard"])

    if st.button("Save Prompt Chain"):
        chains = load_chains()
        chains.append({
            "scenario": scenario,
            "chain": turns,
            "topic": topic,
            "tags": [t.strip() for t in tags.split(",")],
            "intent": intent,
            "difficulty": difficulty,
        })
        save_chains(chains)
        st.success("✅ Prompt Chain Saved")

def prompt_filter_ui():
    st.subheader("🔍 Explore Prompt Chains")
    chains = load_chains()
    tag = st.text_input("Filter by tag")

    topics = sorted(set(c.get("topic", "") for c in chains if c.get("topic")))
    selected_topic = st.selectbox("Filter by topic", [""] + topics)
    intent = st.selectbox("Filter by intent", ["", "harmless", "manipulative", "coercive", "deceptive"])
    difficulty = st.selectbox("Filter by difficulty", ["", "easy", "moderate", "hard"])

    filtered = [
        c for c in chains if
        (not tag or tag in c.get("tags", [])) and
        (not selected_topic or c.get("topic") == selected_topic) and
        (not intent or c.get("intent") == intent) and
        (not difficulty or c.get("difficulty") == difficulty)
    ]

    for c in filtered:
        st.markdown(f"### {c.get('scenario', 'Unnamed Scenario')}")
        for i, t in enumerate(c.get("chain", [])):
            st.markdown(f"**Turn {i+1}:** {t}")
        st.markdown(f"**Tags:** {', '.join(c.get('tags', []))}")
        st.markdown(f"**Topic:** {c.get('topic', 'Unknown')}")
        st.markdown(f"**Intent:** {c.get('intent', 'N/A')}")
        st.markdown(f"**Difficulty:** {c.get('difficulty', 'N/A')}")
        st.markdown("---")

def model_testing_ui():
    st.subheader("🤖 In-Browser Model Tester")
    chains = load_chains()
    selected_scenario = st.selectbox("Optional: Tag scenario for this test", [""] + [c.get("scenario", "") for c in chains])
    model_choice = st.selectbox("Choose Model", ["OpenAI GPT-4", "Gemini Pro"])
    api_key = st.text_input("Enter API Key", type="password")
    prompt = st.text_area("Prompt to Test")
    enable_llm_eval = st.checkbox("Enable LLM-based Evaluation (GPT-4 only)")

    if st.button("Submit"):
        if not api_key or not prompt:
            st.warning("Both API key and prompt are required.")
            return
        metadata = {"scenario": selected_scenario} if selected_scenario else {}

        try:
            if model_choice == "OpenAI GPT-4":
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                )
                output = response["choices"][0]["message"]["content"]
            else:
                setup_gemini(api_key)
                output = call_gemini(prompt)

            st.text_area("Model Response", value=output, height=200)

            eval_result = evaluate_response(output)
            st.markdown(f"**Keyword Evaluation Score:** {eval_result['score']}")
            st.markdown(f"**Flagged Keywords:** {', '.join(eval_result['flagged_keywords']) or 'None'}")
            st.markdown(f"**Refusal Detected:** {'✅ Yes' if eval_result['refusal_detected'] else '❌ No'}")

            if enable_llm_eval and model_choice == "OpenAI GPT-4":
                st.markdown("Running LLM-based evaluation...")
                smart_eval = llm_self_evaluate(prompt, output, api_key)
                st.markdown(f"**LLM Evaluation Score:** `{smart_eval['score']}`")
                st.markdown(f"**LLM Rationale:** {smart_eval['rationale']}")
                eval_result.update({
                    "llm_score": smart_eval["score"],
                    "llm_rationale": smart_eval["rationale"]
                })

            full_metadata = metadata.copy()
            full_metadata.update(eval_result)
            log_response(prompt, model_choice.lower(), output, source="GUI", metadata=full_metadata)
            st.success("✅ Response logged with evaluation.")
        except Exception as e:
            st.error(f"Model Error: {e}")

def summary_ui():
    st.subheader("📊 Summary & Statistics")
    df = load_results()
    if df.empty:
        st.info("No results yet.")
        return

    for col in ["intent", "difficulty", "llm_score"]:
        if col in df.columns:
            counts = df[col].value_counts()
            st.markdown(f"#### Distribution of {col.capitalize()}")
            fig, ax = plt.subplots()
            ax.bar(counts.index.astype(str), counts.values)
            st.pyplot(fig)

def main():
    st.title("🧠 LLM Adversarial Testing Framework")
    tab = st.sidebar.radio("Navigation", ["Build", "Explore", "Test", "Summary"])

    if tab == "Build":
        prompt_builder_ui()
    elif tab == "Explore":
        prompt_filter_ui()
    elif tab == "Test":
        model_testing_ui()
    elif tab == "Summary":
        summary_ui()

if __name__ == "__main__":
    main()
