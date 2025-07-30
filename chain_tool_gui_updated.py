import streamlit as st
import json
import os

PROMPT_FILE = "prompts/multi_turn_chains.json"

def load_chains():
    if not os.path.exists(PROMPT_FILE):
        return []
    with open(PROMPT_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_chains(chains):
    os.makedirs("prompts", exist_ok=True)
    with open(PROMPT_FILE, "w", encoding="utf-8") as f:
        json.dump(chains, f, indent=2)

def build_chain_ui():
    st.subheader("🔧 Build New Prompt Chain")

    scenario = st.text_input("Scenario title")
    category = st.text_input("Category", value="multi_turn")
    tags = st.text_input("Tags (comma-separated)")
    topics = st.text_input("Topics (comma-separated)")
    difficulty = st.selectbox("Difficulty", ["low", "medium", "high"])
    intent = st.selectbox("Intent", ["harmless", "exploit", "boundary_test"])

    chain = []
    for i in range(10):
        msg = st.text_input(f"Turn {i+1}", key=f"turn_{i}")
        if msg.strip():
            chain.append(msg.strip())

    if st.button("Save Chain"):
        if not scenario or not chain:
            st.warning("Scenario and at least one turn are required.")
            return

        new_chain = {
            "scenario": scenario,
            "category": category,
            "tags": [t.strip() for t in tags.split(",") if t.strip()],
            "topics": [t.strip() for t in topics.split(",") if t.strip()],
            "difficulty": difficulty,
            "intent": intent,
            "chain": chain
        }

        chains = load_chains()
        chains.append(new_chain)
        save_chains(chains)
        st.success("✅ Chain saved successfully!")

def view_chains_ui():
    st.subheader("📚 View All Chains")
    chains = load_chains()
    if not chains:
        st.info("No chains found.")
        return

    for idx, c in enumerate(chains, 1):
        with st.expander(f"{idx}. {c['scenario']} — {c['category']}"):
            st.markdown(f"**Tags**: {', '.join(c.get('tags', []))}")
            st.markdown(f"**Topics**: {', '.join(c.get('topics', []))}")
            st.markdown(f"**Difficulty**: {c.get('difficulty')}, **Intent**: {c.get('intent')}")
            for i, turn in enumerate(c["chain"], 1):
                st.markdown(f"**Turn {i}**: {turn}")

def filter_chains_ui():
    st.subheader("🔍 Filter Chains")

    chains = load_chains()
    if not chains:
        st.info("No chains to filter.")
        return

    all_tags = sorted(set(tag for c in chains for tag in c.get("tags", [])))
    all_topics = sorted(set(topic for c in chains for topic in c.get("topics", [])))
    all_difficulties = sorted(set(c.get("difficulty", "") for c in chains))
    all_intents = sorted(set(c.get("intent", "") for c in chains))

    selected_tags = st.multiselect("Filter by Tags", options=all_tags)
    selected_topics = st.multiselect("Filter by Topics", options=all_topics)
    selected_difficulties = st.multiselect("Filter by Difficulty", options=all_difficulties)
    selected_intents = st.multiselect("Filter by Intent", options=all_intents)

    def match(entry, field, values):
        return any(val in entry.get(field, []) if isinstance(entry.get(field, []), list) else [entry.get(field)] for val in values)

    filtered = [
        c for c in chains
        if (match(c, "tags", selected_tags) if selected_tags else True) and
           (match(c, "topics", selected_topics) if selected_topics else True) and
           (match(c, "difficulty", selected_difficulties) if selected_difficulties else True) and
           (match(c, "intent", selected_intents) if selected_intents else True)
    ]

    if filtered:
        st.success(f"✅ Found {len(filtered)} matching chains.")
        for i, c in enumerate(filtered, 1):
            with st.expander(f"{i}. {c['scenario']}"):
                for j, turn in enumerate(c["chain"], 1):
                    st.markdown(f"**Turn {j}**: {turn}")
        if st.button("Export Filtered to File"):
            output_file = "prompts/filtered_chains.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(filtered, f, indent=2)
            st.success(f"Filtered chains saved to {output_file}")
    else:
        st.warning("No matches found.")

def main():
    st.title("🧠 Adversarial Prompt Chain Builder")

    page = st.sidebar.radio("Choose View", ["Build", "View All", "Filter"])

    if page == "Build":
        build_chain_ui()
    elif page == "View All":
        view_chains_ui()
    elif page == "Filter":
        filter_chains_ui()

if __name__ == "__main__":
    main()
