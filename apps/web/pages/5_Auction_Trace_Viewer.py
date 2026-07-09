import streamlit as st

from apps.web.api_client import api_get, handle_json_error, require_login

current_user = require_login()

st.title("Auction Trace Viewer")
st.caption("Inspect stored auction decisions and candidate-level rejection reasons.")
st.write(f"Signed in as `{current_user['full_name']}` with role `{current_user['role']}`")

auctions_response = api_get("/auctions")
if auctions_response.status_code != 200:
    st.error(handle_json_error(auctions_response, "Could not load auctions."))
    st.stop()

auctions = auctions_response.json()
if not auctions:
    st.info("No auctions available yet.")
    st.stop()

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

summary_cols = st.columns(4)
summary_cols[0].metric("Auction ID", auction["id"])
summary_cols[1].metric("Decision", auction["decision_status"])
summary_cols[2].metric("Winner", auction["winner_campaign_id"] or "No Bid")
summary_cols[3].metric("Clearing Price", auction["clearing_price"] or "0.00")

st.subheader("Candidate Trace")
st.dataframe(auction["candidates"], use_container_width=True)
