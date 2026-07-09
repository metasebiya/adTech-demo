import streamlit as st

from apps.web.api_client import api_get, api_post, handle_json_error, require_login
from apps.web.ui import apply_page_style, format_money, outcome_tone, render_badges, render_hero, render_panel

current_user = require_login()
apply_page_style()

publishers_response = api_get("/publishers")
placements_response = api_get("/placements")

if publishers_response.status_code == 403 or placements_response.status_code == 403:
    st.error("Your role does not have permission to run bid simulations.")
    st.stop()

if publishers_response.status_code != 200 or placements_response.status_code != 200:
    st.error("Could not load inventory required for bid simulation.")
    st.stop()

publishers = publishers_response.json()
placements = placements_response.json()
render_hero(
    "Bid Simulator",
    "Create a realistic request, run the SSP decision flow, and use the resulting candidate trace to explain every accept or reject outcome.",
    "Auction Lab",
    [
        ("Publishers", str(len(publishers))),
        ("Placements", str(len(placements))),
        ("Operator", current_user["full_name"]),
    ],
)
render_badges([("Eligibility Engine", "#0f766e"), ("Auction Ranking", "#1d4ed8"), ("Explainable Output", "#f59e0b")])

publisher_options = {f"{item['name']} (#{item['id']})": item["id"] for item in publishers}
placement_options = {f"{item['name']} (#{item['id']})": item["id"] for item in placements}

render_panel(
    "Simulation Setup",
    "Use a live placement, geo, device, and user identifier to show how targeting, budgets, and frequency caps shape the final outcome.",
    eyebrow="Input",
)
with st.form("bid-simulator-form"):
    selected_publisher = st.selectbox("Publisher", list(publisher_options.keys()))
    selected_placement = st.selectbox("Placement", list(placement_options.keys()))
    country = st.text_input("Country", value="US")
    device_type = st.selectbox("Device Type", ["desktop", "mobile", "tablet", "ctv"])
    user_id = st.text_input("User ID", value="demo-user-001")
    submitted = st.form_submit_button("Run Simulation", type="primary")

if submitted:
    response = api_post(
        "/bid-requests",
        {
            "publisher_id": publisher_options[selected_publisher],
            "placement_id": placement_options[selected_placement],
            "country": country,
            "device_type": device_type,
            "user_id": user_id,
        },
    )
    if response.status_code != 201:
        st.error(handle_json_error(response, "Bid simulation failed."))
        st.stop()

    payload = response.json()
    decision = payload["auction_decision"]
    bid_request = payload["bid_request"]
    _, decision_color = outcome_tone(decision["decision_status"])

    render_hero(
        f"Simulation Completed: Bid Request #{bid_request['id']}",
        "Use the summary below to explain the winner, clearing price, and candidate-level reasoning.",
        "Outcome",
        [
            ("Decision", decision["decision_status"].upper()),
            ("Winner", str(decision["winner_campaign_id"] or "No Bid")),
            ("Reason", decision["decision_reason"]),
        ],
    )
    render_badges([(decision["decision_status"].replace("_", " ").title(), decision_color)])
    result_cols = st.columns(4)
    result_cols[0].metric("Decision", decision["decision_status"])
    result_cols[1].metric("Winner Campaign", decision["winner_campaign_id"] or "No Bid")
    result_cols[2].metric("Clearing Price", format_money(decision["clearing_price"] or "0.00"))
    result_cols[3].metric("Reason", decision["decision_reason"])

    candidates = decision.get("candidates", [])
    eligible = [candidate for candidate in candidates if candidate["eligibility_status"] == "eligible"]
    rejected = [candidate for candidate in candidates if candidate["eligibility_status"] == "rejected"]

    left, right = st.columns(2)
    with left:
        render_panel("Eligible Campaigns", "Campaigns that passed validation and were ranked for the auction.", eyebrow="Accepted")
        st.dataframe(eligible, use_container_width=True)
    with right:
        render_panel("Rejected Campaigns", "Campaigns excluded by targeting, budget, or frequency-cap rules.", eyebrow="Rejected")
        st.dataframe(rejected, use_container_width=True)
