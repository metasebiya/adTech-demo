import plotly.express as px
import streamlit as st

from apps.web.api_client import api_get, handle_json_error, require_login

current_user = require_login()

st.title("Analytics Dashboard")
st.caption("Campaign, publisher, and no-bid analytics built from the backend metrics endpoints.")
st.write(f"Signed in as `{current_user['full_name']}` with role `{current_user['role']}`")

overview_response = api_get("/metrics/overview")
timeseries_response = api_get("/metrics/timeseries")
campaigns_response = api_get("/metrics/campaigns")
publishers_response = api_get("/metrics/publishers")
no_bid_response = api_get("/metrics/no-bid-reasons")

if overview_response.status_code != 200:
    st.error(handle_json_error(overview_response, "Could not load analytics metrics."))
    st.stop()

overview = overview_response.json()
kpis = st.columns(5)
kpis[0].metric("Bid Requests", overview["bid_requests"])
kpis[1].metric("Win Rate", f"{overview['win_rate']:.2%}")
kpis[2].metric("CTR", f"{overview['ctr']:.2%}")
kpis[3].metric("CVR", f"{overview['cvr']:.2%}")
kpis[4].metric("Revenue", overview["revenue"])

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
        chart.update_layout(margin=dict(l=20, r=20, t=60, b=20), legend_title_text="Metric")
        st.plotly_chart(chart, use_container_width=True)

charts_left, charts_right = st.columns(2)

with charts_left:
    st.subheader("Campaign Performance")
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
            revenue_chart.update_layout(margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(revenue_chart, use_container_width=True)
    else:
        st.warning(handle_json_error(campaigns_response, "Could not load campaign metrics."))

with charts_right:
    st.subheader("Publisher Performance")
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
            publisher_chart.update_layout(margin=dict(l=20, r=20, t=60, b=20))
            st.plotly_chart(publisher_chart, use_container_width=True)
    else:
        st.warning(handle_json_error(publishers_response, "Could not load publisher metrics."))

st.subheader("No-Bid Breakdown")
if no_bid_response.status_code == 200:
    no_bid_rows = no_bid_response.json()
    if no_bid_rows:
        pie_chart = px.pie(no_bid_rows, names="reason", values="count", title="No-Bid Reasons")
        pie_chart.update_layout(margin=dict(l=20, r=20, t=60, b=20))
        st.plotly_chart(pie_chart, use_container_width=True)
        st.dataframe(no_bid_rows, use_container_width=True)
    else:
        st.info("No no-bid rows have been generated yet.")
else:
    st.warning(handle_json_error(no_bid_response, "Could not load no-bid reason metrics."))
