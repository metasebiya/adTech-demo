import streamlit as st

from apps.web.api_client import api_get, handle_json_error, require_login
from apps.web.ui import apply_page_style, format_money, render_badges, render_hero, render_panel

current_user = require_login()
apply_page_style()

auctions_response = api_get("/auctions")
if auctions_response.status_code != 200:
    st.error(handle_json_error(auctions_response, "Could not load auctions."))
    st.stop()

auctions = auctions_response.json()
if not auctions:
    st.info("No auctions available yet.")
    st.stop()

render_hero(
    "Auction Trace Viewer",
    "Review historical auction outcomes, then drill into candidate-level reasoning to explain why a campaign won or why the marketplace returned no bid.",
    "Decision Forensics",
    [
        ("Available Auctions", str(len(auctions))),
        ("Role", current_user["role"].upper()),
        ("Operator", current_user["full_name"]),
    ],
)
render_panel(
    "How To Use This View",
    "Select an auction below to inspect the final decision, winning price, and each candidate's eligibility path.",
    eyebrow="Workflow",
)
auction_options = {
    f"Auction #{auction['id']} | {auction['decision_status']} | winner {auction['winner_campaign_id']}": auction["id"]
    for auction in auctions
}
selected_label = st.selectbox("Select Auction", list(auction_options.keys()))
selected_id = auction_options[selected_label]

auction_response = api_get(f"/auctions/{selected_id}")
if auction_response.status_code != 200:
    st.error(handle_json_error(auction_response, "Could not load auction details."))
    st.stop()

auction = auction_response.json()
render_badges(
    [
        (auction["decision_status"].replace("_", " ").title(), "#0f766e" if auction["winner_campaign_id"] else "#dc2626"),
        (f"Winner {auction['winner_campaign_id'] or 'No Bid'}", "#1d4ed8"),
    ]
)

summary_cols = st.columns(4)
summary_cols[0].metric("Auction ID", auction["id"])
summary_cols[1].metric("Decision", auction["decision_status"])
summary_cols[2].metric("Winner", auction["winner_campaign_id"] or "No Bid")
summary_cols[3].metric("Clearing Price", format_money(auction["clearing_price"] or "0.00"))

render_panel("Candidate Trace", "Use this table to narrate which campaigns were eligible, which were rejected, and the specific rejection reasons.", eyebrow="Diagnostic Detail")
st.dataframe(auction["candidates"], use_container_width=True)
