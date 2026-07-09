import requests
import plotly.graph_objects as go
import streamlit as st

from apps.web.api_client import api_get
from apps.web.ui import apply_chart_theme, apply_page_style, format_money, render_badges, render_hero, render_panel
from core.config import get_settings

settings = get_settings()

st.set_page_config(page_title="AdTech Demo", page_icon="AD", layout="wide")
apply_page_style()

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
    current_user = st.session_state.current_user
    me_response = api_get("/auth/me")
    metrics_response = api_get("/metrics/overview")
    hero_stats = [("Signed In As", current_user["full_name"]), ("Role", current_user["role"].upper())]
    if me_response.status_code == 200:
        hero_stats.append(("Session", "Validated"))
    else:
        hero_stats.append(("Session", "Needs Refresh"))
    render_hero(
        "AdTech Demo Command Center",
        "A client-ready SSP workflow experience for campaign operations, bid simulations, auction diagnostics, and performance analytics.",
        "Presentation Mode",
        hero_stats,
    )
    render_badges(
        [
            ("Inventory", "#0f766e"),
            ("Auctions", "#1d4ed8"),
            ("Events", "#f59e0b"),
            ("Analytics", "#172033"),
        ]
    )
    if metrics_response.status_code == 200:
        metrics = metrics_response.json()
        top_cols = st.columns(4)
        top_cols[0].metric("Bid Requests", metrics["bid_requests"])
        top_cols[1].metric("Wins", metrics["wins"])
        top_cols[2].metric("Impressions", metrics["impressions"])
        top_cols[3].metric("Revenue", format_money(metrics["revenue"]))

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
                        line=dict(width=3),
                        marker=dict(size=8),
                    )
                )
                apply_chart_theme(chart).update_layout(
                    title="Marketplace Activity Overview",
                    yaxis=dict(title="Bid Requests"),
                    yaxis2=dict(title="Revenue", overlaying="y", side="right"),
                )
                st.plotly_chart(chart, use_container_width=True)
    else:
        st.info("Use the sidebar to open the manager and explorer pages for the current demo slice.")

    left, right = st.columns([1.3, 1])
    with left:
        render_panel(
            "Demo Flow",
            "<ol class='adtech-list'><li>Manage campaigns and inventory.</li><li>Run a bid simulation.</li><li>Inspect the auction trace.</li><li>Review events and analytics.</li></ol>",
            eyebrow="Suggested Walkthrough",
        )
    with right:
        render_panel(
            "Available Pages",
            "<ul class='adtech-list'><li>Publisher & Placement Manager</li><li>Campaign Manager</li><li>Home Overview</li><li>Bid Simulator</li><li>Auction Trace Viewer</li><li>Event Explorer</li><li>Analytics Dashboard</li></ul>",
            eyebrow="Navigation",
        )
    if st.button("Log out", type="secondary"):
        st.session_state.access_token = None
        st.session_state.current_user = None
        st.rerun()
else:
    render_hero(
        "AdTech Demo Platform",
        "Professional SSP-side workflow storytelling for client presentations, from targeted demand evaluation to delivery analytics.",
        "Client Demo",
        [("Stack", "FastAPI + Streamlit"), ("Focus", "SSP Bid Workflow"), ("Runtime", "Local Demo Ready")],
    )
    intro_left, intro_right = st.columns([1.1, 0.9])
    with intro_left:
        render_panel(
            "What This Demo Shows",
            "<ul class='adtech-list'><li>Role-based access for ad operations and analysis.</li><li>Bid request simulation with explainable auction decisions.</li><li>Event ingestion and analytics dashboards.</li></ul>",
            eyebrow="Overview",
        )
    with intro_right:
        with st.form("login-form"):
            st.markdown("### Sign In")
            email = st.text_input("Email", placeholder="admin@adtech-demo.local")
            password = st.text_input("Password", type="password", placeholder="ChangeMe123!")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
    if submitted:
        ok, error = authenticate(email=email, password=password)
        if ok:
            st.rerun()
        st.error(error or "Login failed")

st.caption("Current demo slice: authentication, inventory and campaign management, bid simulation, auction traces, event exploration, and analytics dashboards.")
