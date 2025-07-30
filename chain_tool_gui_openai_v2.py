import os
import streamlit as st
from dotenv import load_dotenv
from framework.evaluation_utils_openai_v1 import evaluate_response, llm_self_evaluate
from framework.utils import generate_gemini_response, log_result

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

st.set_page_config(page_title="LLM Adversarial Test Framework", layout="wide")

tabs = ["Build", "Explore", "Test", "Summary"]
selected_tab = st.sidebar.radio("Navigation", tabs)

# --- Build Tab ---
if selected_tab == "Build":
    st.header("Prompt Builder (Chained)")

    scenario = st.text_input("Scenario Title")
    turn1 = st.text_area("Turn 1 Prompt")
    turn2 = st.text_area("Turn 2 Prompt")

    tags = st.text_input("Tags (comma-separated)").lower().split(",")
    topic = st.text_input("Topic").lower()
    intent = st.selectbox("Intent", ["harmless", "manipulative", "exploitative"])
    difficulty = st.selectbox("Difficulty", ["easy", "moderate", "hard"])

    if st.button("Save Scenario"):
        from framework.utils import save_prompt
        save_prompt(scenario, turn1, turn2, tags, topic, intent, difficulty)
        st.success("Prompt saved!")

# --- Explore Tab ---
elif selected_tab == "Explore":
    from framework.utils import load_prompts
    prompts = load_prompts()

    st.header("Prompt Explorer")
    topics = list({p["topic"] for p in prompts if p["topic"]})
    intents = list({p["intent"] for p in prompts})
    difficulties = list({p["difficulty"] for p in prompts})

    selected_topic = st.selectbox("Filter by Topic", ["All"] + topics)
    selected_intent = st.selectbox("Filter by Intent", ["All"] + intents)
    selected_difficulty = st.selectbox("Filter by Difficulty", ["All"] + difficulties)

    for c in prompts:
        if ((selected_topic == "All" or c["topic"] == selected_topic) and
            (selected_intent == "All" or c["intent"] == selected_intent) and
            (selected_difficulty == "All" or c["difficulty"] == selected_difficulty)):
            st.markdown(f"### {c['scenario'] or 'Unnamed Scenario'}")
            st.write(f"**Turn 1:** {c['turn_1']}")
            st.write(f"**Turn 2:** {c['turn_2']}")
            st.write(f"**Tags:** {', '.join(c['tags'])}")
            st.write(f"**Topic:** {c['topic']}")
            st.write(f"**Intent:** {c['intent']}")
            st.write(f"**Difficulty:** {c['difficulty']}")
            st.markdown("---")

# --- Test Tab ---
elif selected_tab == "Test":
    st.header("Adversarial Test Runner")

    selected_model = st.selectbox("Select Model:", ["OpenAI GPT-4", "Gemini Pro"])

    if selected_model == "OpenAI GPT-4":
        gpt_model = st.selectbox(
            "Select GPT Model:",
            ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
            index=0
        )
    elif selected_model == "Gemini Pro":
        gpt_model = st.selectbox(
            "Select Gemini Model:",
            ["gemini-pro", "gemini-pro-vision"],
            index=0
        )

    prompt = st.text_area("Enter a test prompt", height=150)
    enable_keyword_eval = st.checkbox("Enable keyword evaluation", value=True)
    enable_smart_eval = st.checkbox("Enable smart LLM evaluation (OpenAI only)", value=True)

    submit_button = st.button("Submit")

    if submit_button and prompt:
        if selected_model == "OpenAI GPT-4":
            try:
                from openai import OpenAI
                client = OpenAI(api_key=OPENAI_API_KEY)
                response = client.chat.completions.create(
                    model=gpt_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                model_output = response.choices[0].message.content
            except Exception as e:
                st.error(f"OpenAI Error: {e}")
                model_output = ""

        elif selected_model == "Gemini Pro":
            try:
                model_output = generate_gemini_response(gpt_model, prompt, GOOGLE_API_KEY)
            except Exception as e:
                st.error(f"Gemini Error: {e}")
                model_output = ""

        if model_output:
            st.markdown("### Model Output")
            st.write(model_output)

            keyword_results = evaluate_response(model_output) if enable_keyword_eval else {}
            smart_results = llm_self_evaluate(prompt, model_output, OPENAI_API_KEY) if enable_smart_eval and selected_model == "OpenAI GPT-4" else {}

            st.markdown("### Evaluation Results")
            if keyword_results:
                st.write("**Keyword Evaluation:**", keyword_results)
            if smart_results:
                st.write("**Smart Evaluation:**", smart_results)

            log_result(prompt, model_output, selected_model, keyword_results, smart_results, gpt_model)

# --- Summary Tab ---
elif selected_tab == "Summary":
    import pandas as pd
    import matplotlib.pyplot as plt

    st.header("Evaluation Summary")

    try:
        df = pd.read_csv("results/model_responses.csv")
        st.dataframe(df.tail(10))

        st.markdown("### Breakdown by Intent")
        st.bar_chart(df["intent"].value_counts())

        st.markdown("### Breakdown by Model")
        st.bar_chart(df["model_used"].value_counts())

        st.markdown("### Risk Scores (Smart Eval)")
        if "smart_score" in df.columns:
            st.line_chart(df["smart_score"].dropna())

    except FileNotFoundError:
        st.warning("No results logged yet.")