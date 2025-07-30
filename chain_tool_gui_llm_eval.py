import streamlit as st
import json
import os
import openai
from datetime import datetime
from framework.gemini_model_utils import setup_gemini, call_gemini
from framework.response_logging_utils import log_response
from framework.evaluation_utils import evaluate_response, llm_self_evaluate

PROMPT_FILE = "prompts/multi_turn_chains.json"

def load_chains():
    if not os.path.exists(PROMPT_FILE):
        return []
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def model_testing_ui():
    st.subheader("🤖 In-Browser Model Tester (Smart Evaluation)")
    chains = load_chains()
    selected_scenario = st.selectbox("Optional: Tag scenario for this test", [""] + [c["scenario"] for c in chains])
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

            elif model_choice == "Gemini Pro":
                setup_gemini(api_key)
                output = call_gemini(prompt)

            st.text_area("Model Response", value=output, height=200)

            # Keyword-based evaluation
            eval_result = evaluate_response(output)
            st.markdown(f"**Keyword Evaluation Score:** {eval_result['score']}")
            st.markdown(f"**Flagged Keywords:** {', '.join(eval_result['flagged_keywords']) or 'None'}")
            st.markdown(f"**Refusal Detected:** {'✅ Yes' if eval_result['refusal_detected'] else '❌ No'}")

            # Optional LLM-based evaluation
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

def main():
    st.title("🧠 Adversarial Prompt Chain Tester (with Smart Evaluation)")
    model_testing_ui()

if __name__ == "__main__":
    main()
