import streamlit as st

from apps.web.api_client import api_get, handle_json_error, require_login
from apps.web.ui import apply_page_style, render_hero, render_panel

current_user = require_login()
apply_page_style()

campaigns_response = api_get("/campaigns")
auctions_response = api_get("/auctions")
publishers_response = api_get("/publishers")

params: dict[str, int] = {}
render_hero(
    "Event Explorer",
    "Browse impression, click, and conversion records to connect delivery behavior back to the auction decisions that produced it.",
    "Delivery Signals",
    [
        ("Role", current_user["role"].upper()),
        ("Auction Filters", "Enabled"),
        ("Mode", "Read Exploration"),
    ],
)
render_panel(
    "Filter The Story",
    "Narrow the dataset by campaign, auction, or publisher to demonstrate how post-auction engagement lines up with targeting and winning logic.",
    eyebrow="Controls",
)

filter_col_1, filter_col_2, filter_col_3 = st.columns(3)

campaign_options = {"All Campaigns": None}
if campaigns_response.status_code == 200:
    campaign_options.update(
        {f"{campaign['name']} (#{campaign['id']})": campaign["id"] for campaign in campaigns_response.json()}
    )
with filter_col_1:
    selected_campaign = st.selectbox("Campaign", list(campaign_options.keys()))
    if campaign_options[selected_campaign] is not None:
        params["campaign_id"] = campaign_options[selected_campaign]
    elif campaigns_response.status_code == 403:
        st.caption("Campaign filter unavailable for your role.")

auction_options = {"All Auctions": None}
if auctions_response.status_code == 200:
    auction_options.update({f"Auction #{auction['id']}": auction["id"] for auction in auctions_response.json()})
with filter_col_2:
    selected_auction = st.selectbox("Auction", list(auction_options.keys()))
    if auction_options[selected_auction] is not None:
        params["auction_decision_id"] = auction_options[selected_auction]

publisher_options = {"All Publishers": None}
if publishers_response.status_code == 200:
    publisher_options.update(
        {f"{publisher['name']} (#{publisher['id']})": publisher["id"] for publisher in publishers_response.json()}
    )
with filter_col_3:
    selected_publisher = st.selectbox("Publisher", list(publisher_options.keys()))
    if publisher_options[selected_publisher] is not None:
        params["publisher_id"] = publisher_options[selected_publisher]
    elif publishers_response.status_code == 403:
        st.caption("Publisher filter unavailable for your role.")

events_response = api_get("/events", params=params)
if events_response.status_code == 403:
    st.error("Your role does not have permission to view event records.")
    st.stop()

if events_response.status_code != 200:
    st.error(handle_json_error(events_response, "Could not load events."))
    st.stop()

events = events_response.json()
render_panel("Event Feed", "Chronological view of recorded impressions, clicks, and conversions for demo analysis.", eyebrow="Results")
st.dataframe(events, use_container_width=True)
