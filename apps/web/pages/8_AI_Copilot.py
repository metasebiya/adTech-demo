import streamlit as st

from apps.web.api_client import api_get, api_post, handle_json_error, require_login
from apps.web.ui import apply_page_style, render_badges, render_hero, render_panel

current_user = require_login()
apply_page_style()

st.session_state.setdefault("copilot_prompt", "")

render_hero(
    "AI Copilot",
    "A bounded internal copilot that inspects auctions, campaign performance, and metrics to explain what happened and what operations should do next.",
    "Workflow Intelligence",
    [
        ("Operator", current_user["full_name"]),
        ("Role", current_user["role"].upper()),
        ("Mode", "Explain + Recommend"),
    ],
)
render_badges([("Auctions", "#1d4ed8"), ("Metrics", "#0f766e"), ("Operations", "#f59e0b")])

questions_response = api_get("/copilot/suggested-questions")
if questions_response.status_code == 403:
    st.error("Your role does not have permission to use the AI copilot.")
    st.stop()
if questions_response.status_code != 200:
    st.error(handle_json_error(questions_response, "Could not load copilot prompts."))
    st.stop()

questions = questions_response.json()
render_panel(
    "Suggested Questions",
    "Use a prompt below or write your own question about auctions, no-bids, campaigns, or analytics.",
    eyebrow="Prompt Library",
)

question_columns = st.columns(2)
for index, item in enumerate(questions):
    with question_columns[index % 2]:
        if st.button(item["question"], use_container_width=True):
            st.session_state["copilot_prompt"] = item["question"]

with st.form("copilot-query-form"):
    query = st.text_area(
        "Ask the copilot",
        value=st.session_state.get("copilot_prompt", ""),
        placeholder="Why did auction 1 select its winner?",
        height=150,
    )
    submitted = st.form_submit_button("Generate Insight", type="primary", use_container_width=True)

if submitted:
    st.session_state["copilot_prompt"] = query
    response = api_post("/copilot/query", {"query": query})
    if response.status_code != 200:
        st.error(handle_json_error(response, "Copilot query failed."))
        st.stop()

    payload = response.json()
    render_hero(
        payload["title"],
        payload["answer"],
        payload["mode"].replace("_", " ").title(),
        [("Sources", str(len(payload["inspected_sources"]))), ("Actions", str(len(payload["recommended_actions"])))],
    )

    left, right = st.columns(2)
    with left:
        render_panel("Supporting Facts", "", eyebrow="Evidence")
        for fact in payload["supporting_facts"]:
            st.markdown(f"- {fact}")
    with right:
        render_panel("Recommended Actions", "", eyebrow="Next Steps")
        for action in payload["recommended_actions"]:
            st.markdown(f"- {action}")

    render_panel("Inspected Sources", ", ".join(payload["inspected_sources"]), eyebrow="Traceability")
