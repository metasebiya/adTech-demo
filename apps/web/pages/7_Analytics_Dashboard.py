import plotly.express as px
import streamlit as st

from apps.web.api_client import api_get, handle_json_error, require_login
from apps.web.ui import apply_chart_theme, apply_page_style, format_money, render_badges, render_hero, render_panel

current_user = require_login()
apply_page_style()

overview_response = api_get("/metrics/overview")
timeseries_response = api_get("/metrics/timeseries")
campaigns_response = api_get("/metrics/campaigns")
publishers_response = api_get("/metrics/publishers")
no_bid_response = api_get("/metrics/no-bid-reasons")

if overview_response.status_code != 200:
    st.error(handle_json_error(overview_response, "Could not load analytics metrics."))
    st.stop()

overview = overview_response.json()
render_hero(
    "Analytics Dashboard",
    "Client-facing performance analytics built from the SSP event trail, highlighting demand quality, delivery outcomes, and marketplace inefficiencies.",
    "Performance Intelligence",
    [
        ("Operator", current_user["full_name"]),
        ("Revenue", format_money(overview["revenue"])),
        ("Win Rate", f"{overview['win_rate']:.2%}"),
    ],
)
render_badges([("Campaign Lens", "#1d4ed8"), ("Publisher Lens", "#0f766e"), ("No-Bid Lens", "#f59e0b")])
kpis = st.columns(5)
kpis[0].metric("Bid Requests", overview["bid_requests"])
kpis[1].metric("Win Rate", f"{overview['win_rate']:.2%}")
kpis[2].metric("CTR", f"{overview['ctr']:.2%}")
kpis[3].metric("CVR", f"{overview['cvr']:.2%}")
kpis[4].metric("Revenue", format_money(overview["revenue"]))

if timeseries_response.status_code == 200:
    timeseries = timeseries_response.json()
    if timeseries:
        chart = px.line(
            timeseries,
            x="date",
            y=["wins", "impressions", "clicks", "conversions"],
            markers=True,
            title="Delivery Trend",
        )
        apply_chart_theme(chart).update_layout(legend_title_text="Metric")
        st.plotly_chart(chart, use_container_width=True)

charts_left, charts_right = st.columns(2)

with charts_left:
    render_panel("Campaign Performance", "Compare campaign-level wins, engagement, and revenue outcomes to discuss which demand sources are strongest.", eyebrow="Campaign Lens")
    if campaigns_response.status_code == 200:
        campaigns = campaigns_response.json()
        st.dataframe(campaigns, use_container_width=True)
        if campaigns:
            revenue_chart = px.bar(
                campaigns,
                x="campaign_name",
                y="revenue",
                title="Revenue by Campaign",
                text="revenue",
            )
            apply_chart_theme(revenue_chart)
            st.plotly_chart(revenue_chart, use_container_width=True)
    else:
        st.warning(handle_json_error(campaigns_response, "Could not load campaign metrics."))

with charts_right:
    render_panel("Publisher Performance", "Review where marketplace demand is concentrated and which inventory sources are generating the strongest commercial return.", eyebrow="Publisher Lens")
    if publishers_response.status_code == 200:
        publishers = publishers_response.json()
        st.dataframe(publishers, use_container_width=True)
        if publishers:
            publisher_chart = px.bar(
                publishers,
                x="publisher_name",
                y="bid_requests",
                color="revenue",
                title="Bid Requests by Publisher",
            )
            apply_chart_theme(publisher_chart)
            st.plotly_chart(publisher_chart, use_container_width=True)
    else:
        st.warning(handle_json_error(publishers_response, "Could not load publisher metrics."))

render_panel("No-Bid Breakdown", "Explain lost opportunity by showing which rule most often prevented demand from clearing.", eyebrow="Optimization Lens")
if no_bid_response.status_code == 200:
    no_bid_rows = no_bid_response.json()
    if no_bid_rows:
        pie_chart = px.pie(no_bid_rows, names="reason", values="count", title="No-Bid Reasons")
        apply_chart_theme(pie_chart)
        st.plotly_chart(pie_chart, use_container_width=True)
        st.dataframe(no_bid_rows, use_container_width=True)
    else:
        st.info("No no-bid rows have been generated yet.")
else:
    st.warning(handle_json_error(no_bid_response, "Could not load no-bid reason metrics."))
