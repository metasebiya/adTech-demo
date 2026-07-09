import requests
import plotly.graph_objects as go
import streamlit as st

from apps.web.api_client import api_get
from core.config import get_settings

settings = get_settings()

st.set_page_config(page_title="AdTech Demo", page_icon="AD", layout="centered")
st.title("AdTech Demo Platform")
st.caption("SSP-side bid workflow demo")

if "access_token" not in st.session_state:
    st.session_state.access_token = None
if "current_user" not in st.session_state:
    st.session_state.current_user = None


def authenticate(email: str, password: str) -> tuple[bool, str | None]:
    response = requests.post(
        f"{settings.api_base_url}/auth/login",
        json={"email": email, "password": password},
        timeout=10,
    )
    if response.status_code != 200:
        detail = response.json().get("detail", "Login failed")
        return False, detail
    payload = response.json()
    st.session_state.access_token = payload["access_token"]
    st.session_state.current_user = payload["user"]
    return True, None


if st.session_state.access_token:
    st.success(f"Signed in as {st.session_state.current_user['full_name']}")
    st.write(f"Role: `{st.session_state.current_user['role']}`")
    me_response = api_get("/auth/me")
    if me_response.status_code == 200:
        st.caption("Backend session validated")
    else:
        st.warning("Stored session could not be validated against the backend.")
    metrics_response = api_get("/metrics/overview")
    if metrics_response.status_code == 200:
        metrics = metrics_response.json()
        top_cols = st.columns(4)
        top_cols[0].metric("Bid Requests", metrics["bid_requests"])
        top_cols[1].metric("Wins", metrics["wins"])
        top_cols[2].metric("Impressions", metrics["impressions"])
        top_cols[3].metric("Revenue", metrics["revenue"])

        bottom_cols = st.columns(4)
        bottom_cols[0].metric("No-Bids", metrics["no_bids"])
        bottom_cols[1].metric("CTR", f"{metrics['ctr']:.2%}")
        bottom_cols[2].metric("CVR", f"{metrics['cvr']:.2%}")
        bottom_cols[3].metric("Win Rate", f"{metrics['win_rate']:.2%}")

        timeseries_response = api_get("/metrics/timeseries")
        if timeseries_response.status_code == 200:
            timeseries = timeseries_response.json()
            if timeseries:
                chart = go.Figure()
                chart.add_trace(
                    go.Bar(
                        x=[row["date"] for row in timeseries],
                        y=[row["bid_requests"] for row in timeseries],
                        name="Bid Requests",
                    )
                )
                chart.add_trace(
                    go.Scatter(
                        x=[row["date"] for row in timeseries],
                        y=[row["revenue"] for row in timeseries],
                        name="Revenue",
                        mode="lines+markers",
                        yaxis="y2",
                    )
                )
                chart.update_layout(
                    title="Bid Requests and Revenue",
                    yaxis=dict(title="Bid Requests"),
                    yaxis2=dict(title="Revenue", overlaying="y", side="right"),
                    margin=dict(l=20, r=20, t=60, b=20),
                    legend=dict(orientation="h"),
                )
                st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("Use the sidebar to open the manager and explorer pages for the current demo slice.")

    st.info(
        "Available demo pages: Publisher & Placement Manager, Campaign Manager, Home Overview, Bid Simulator, Auction Trace Viewer, Event Explorer, and Analytics Dashboard."
    )
    if st.button("Log out", type="secondary"):
        st.session_state.access_token = None
        st.session_state.current_user = None
        st.rerun()
else:
    with st.form("login-form"):
        email = st.text_input("Email", placeholder="admin@adtech-demo.local")
        password = st.text_input("Password", type="password", placeholder="ChangeMe123!")
        submitted = st.form_submit_button("Sign in", type="primary")
    if submitted:
        ok, error = authenticate(email=email, password=password)
        if ok:
            st.rerun()
        st.error(error or "Login failed")

st.divider()
st.markdown(
    "Current demo slice: authentication, inventory and campaign management, bid simulation, auction traces, event exploration, and analytics dashboards."
)
