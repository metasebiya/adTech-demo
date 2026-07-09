import plotly.express as px
import streamlit as st

from apps.web.api_client import api_get, handle_json_error, require_login
from apps.web.ui import apply_chart_theme, apply_page_style, format_money, render_hero, render_panel

current_user = require_login()
apply_page_style()

overview_response = api_get("/metrics/overview")
timeseries_response = api_get("/metrics/timeseries")
auctions_response = api_get("/auctions")
events_response = api_get("/events")

if overview_response.status_code != 200:
    st.error(handle_json_error(overview_response, "Could not load overview metrics."))
    st.stop()

overview = overview_response.json()
render_hero(
    "Home Overview",
    "A concise executive readout of marketplace activity, recent delivery, and the most important signals to discuss during the demo.",
    "Executive Snapshot",
    [
        ("Operator", current_user["full_name"]),
        ("Role", current_user["role"].upper()),
        ("Revenue", format_money(overview["revenue"])),
    ],
)
top = st.columns(4)
top[0].metric("Bid Requests", overview["bid_requests"])
top[1].metric("Wins", overview["wins"])
top[2].metric("Impressions", overview["impressions"])
top[3].metric("Revenue", format_money(overview["revenue"]))

mid = st.columns(4)
mid[0].metric("No-Bids", overview["no_bids"])
mid[1].metric("Clicks", overview["clicks"])
mid[2].metric("Conversions", overview["conversions"])
mid[3].metric("Win Rate", f"{overview['win_rate']:.2%}")

if timeseries_response.status_code == 200:
    timeseries = timeseries_response.json()
    if timeseries:
        chart = px.area(
            timeseries,
            x="date",
            y=["bid_requests", "wins", "impressions"],
            title="Marketplace Momentum",
        )
        apply_chart_theme(chart)
        st.plotly_chart(chart, use_container_width=True)

highlight_left, highlight_right = st.columns([1.2, 1])
with highlight_left:
    render_panel(
        "Storyline For Client Walkthrough",
        "<ul class='adtech-list'><li>Open with market demand and win rate.</li><li>Use Bid Simulator to explain eligibility logic.</li><li>Use Analytics Dashboard to close with impact and revenue.</li></ul>",
        eyebrow="Suggested Flow",
    )
with highlight_right:
    render_panel(
        "Health Signals",
        f"<ul class='adtech-list'><li>CTR: {overview['ctr']:.2%}</li><li>CVR: {overview['cvr']:.2%}</li><li>No-Bid Rate: {overview['no_bid_rate']:.2%}</li></ul>",
        eyebrow="Performance",
    )

col_left, col_right = st.columns(2)

with col_left:
    render_panel("Recent Auctions", "Most recent decisions and outcomes from the simulated auction flow.", eyebrow="Activity")
    if auctions_response.status_code == 200:
        auctions = auctions_response.json()[:10]
        st.dataframe(auctions, use_container_width=True)
    else:
        st.warning(handle_json_error(auctions_response, "Could not load recent auctions."))

with col_right:
    render_panel("Recent Events", "Fresh delivery signals across impressions, clicks, and conversions.", eyebrow="Delivery")
    if events_response.status_code == 200:
        events = events_response.json()[:10]
        st.dataframe(events, use_container_width=True)
    elif events_response.status_code == 403:
        st.info("Your role can view dashboard metrics, but not event records.")
    else:
        st.warning(handle_json_error(events_response, "Could not load recent events."))
