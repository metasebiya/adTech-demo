import plotly.express as px
import streamlit as st

from apps.web.api_client import api_get, handle_json_error, require_login

current_user = require_login()

st.title("Home Overview")
st.caption("High-level KPI dashboard for the current SSP demo slice.")
st.write(f"Signed in as `{current_user['full_name']}` with role `{current_user['role']}`")

overview_response = api_get("/metrics/overview")
timeseries_response = api_get("/metrics/timeseries")
auctions_response = api_get("/auctions")
events_response = api_get("/events")

if overview_response.status_code != 200:
    st.error(handle_json_error(overview_response, "Could not load overview metrics."))
    st.stop()

overview = overview_response.json()
top = st.columns(4)
top[0].metric("Bid Requests", overview["bid_requests"])
top[1].metric("Wins", overview["wins"])
top[2].metric("Impressions", overview["impressions"])
top[3].metric("Revenue", overview["revenue"])

mid = st.columns(4)
mid[0].metric("No-Bids", overview["no_bids"])
mid[1].metric("Clicks", overview["clicks"])
mid[2].metric("Conversions", overview["conversions"])
mid[3].metric("Win Rate", f"{overview['win_rate']:.2%}")

if timeseries_response.status_code == 200:
    timeseries = timeseries_response.json()
    if timeseries:
        chart = px.bar(timeseries, x="date", y="bid_requests", title="Daily Bid Requests")
        chart.update_layout(margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(chart, use_container_width=True)

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Recent Auctions")
    if auctions_response.status_code == 200:
        auctions = auctions_response.json()[:10]
        st.dataframe(auctions, use_container_width=True)
    else:
        st.warning(handle_json_error(auctions_response, "Could not load recent auctions."))

with col_right:
    st.subheader("Recent Events")
    if events_response.status_code == 200:
        events = events_response.json()[:10]
        st.dataframe(events, use_container_width=True)
    elif events_response.status_code == 403:
        st.info("Your role can view dashboard metrics, but not event records.")
    else:
        st.warning(handle_json_error(events_response, "Could not load recent events."))
