from __future__ import annotations

from decimal import Decimal
from html import escape
from typing import Any

import plotly.graph_objects as go
import streamlit as st

COLORWAY = ["#0f766e", "#f59e0b", "#1d4ed8", "#dc2626", "#7c3aed"]


def apply_page_style() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #f4efe7;
            --panel: rgba(255, 255, 255, 0.78);
            --panel-strong: rgba(255, 255, 255, 0.94);
            --text: #172033;
            --muted: #5d6473;
            --line: rgba(23, 32, 51, 0.08);
            --navy: #172033;
            --teal: #0f766e;
            --amber: #f59e0b;
            --blue: #1d4ed8;
            --danger: #dc2626;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(15, 118, 110, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(245, 158, 11, 0.18), transparent 24%),
                linear-gradient(180deg, #f7f3eb 0%, #ece7df 100%);
            color: var(--text);
            font-family: Aptos, "Segoe UI", "Trebuchet MS", sans-serif;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1220px;
        }

        h1, h2, h3 {
            color: var(--navy);
            letter-spacing: -0.02em;
        }

        [data-testid="stMetric"] {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 0.9rem 1rem;
            box-shadow: 0 18px 40px rgba(23, 32, 51, 0.07);
            backdrop-filter: blur(8px);
        }

        [data-testid="stMetricLabel"] {
            color: var(--muted);
            font-weight: 600;
        }

        [data-testid="stMetricValue"] {
            color: var(--navy);
        }

        .adtech-hero {
            background:
                linear-gradient(135deg, rgba(23, 32, 51, 0.96), rgba(15, 118, 110, 0.92)),
                linear-gradient(180deg, rgba(245, 158, 11, 0.12), transparent);
            color: #f8fafc;
            border-radius: 28px;
            padding: 1.6rem 1.7rem;
            box-shadow: 0 26px 56px rgba(23, 32, 51, 0.18);
            margin-bottom: 1rem;
        }

        .adtech-hero h1, .adtech-hero h2, .adtech-hero h3, .adtech-hero p {
            color: #f8fafc !important;
            margin: 0;
        }

        .adtech-kicker {
            display: inline-block;
            padding: 0.32rem 0.7rem;
            border-radius: 999px;
            background: rgba(255, 255, 255, 0.14);
            border: 1px solid rgba(255, 255, 255, 0.22);
            font-size: 0.8rem;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            margin-bottom: 0.7rem;
        }

        .adtech-panel {
            background: var(--panel-strong);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1.1rem;
            box-shadow: 0 18px 38px rgba(23, 32, 51, 0.07);
            margin-bottom: 1rem;
        }

        .adtech-panel h3, .adtech-panel h4, .adtech-panel p {
            margin-top: 0;
        }

        .adtech-eyebrow {
            color: var(--muted);
            font-size: 0.84rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.35rem;
        }

        .adtech-stat-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 0.8rem;
            margin-top: 0.9rem;
        }

        .adtech-stat {
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 18px;
            padding: 0.85rem 0.9rem;
        }

        .adtech-stat-label {
            opacity: 0.78;
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .adtech-stat-value {
            margin-top: 0.15rem;
            font-size: 1.35rem;
            font-weight: 700;
        }

        .adtech-pill {
            display: inline-block;
            border-radius: 999px;
            padding: 0.28rem 0.7rem;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.03em;
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
            color: white;
        }

        .adtech-list {
            margin: 0;
            padding-left: 1rem;
            color: var(--muted);
        }

        .stDataFrame, [data-testid="stTable"] {
            border-radius: 18px;
            overflow: hidden;
            border: 1px solid var(--line);
        }

        [data-testid="stForm"] {
            background: var(--panel-strong);
            border: 1px solid var(--line);
            border-radius: 22px;
            padding: 1rem 1rem 0.25rem 1rem;
            box-shadow: 0 18px 38px rgba(23, 32, 51, 0.06);
        }

        [data-testid="stSidebar"] {
            background: rgba(250, 248, 244, 0.98);
            border-right: 1px solid rgba(23, 32, 51, 0.06);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero(
    title: str,
    subtitle: str,
    kicker: str,
    stats: list[tuple[str, str]] | None = None,
) -> None:
    stat_html = ""
    if stats:
        cards = "".join(
            f"<div class='adtech-stat'><div class='adtech-stat-label'>{escape(label)}</div><div class='adtech-stat-value'>{escape(value)}</div></div>"
            for label, value in stats
        )
        stat_html = f"<div class='adtech-stat-grid'>{cards}</div>"
    st.markdown(
        f"""
        <section class="adtech-hero">
            <div class="adtech-kicker">{escape(kicker)}</div>
            <h1>{escape(title)}</h1>
            <p style="margin-top:0.55rem; max-width: 820px; line-height: 1.5;">{escape(subtitle)}</p>
            {stat_html}
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_panel(title: str, body: str, eyebrow: str | None = None) -> None:
    eyebrow_html = f"<div class='adtech-eyebrow'>{escape(eyebrow)}</div>" if eyebrow else ""
    st.markdown(
        f"<section class='adtech-panel'>{eyebrow_html}<h3>{escape(title)}</h3><p>{body}</p></section>",
        unsafe_allow_html=True,
    )


def render_badges(items: list[tuple[str, str]]) -> None:
    badge_html = "".join(
        f"<span class='adtech-pill' style='background:{escape(color)}'>{escape(label)}</span>"
        for label, color in items
    )
    st.markdown(badge_html, unsafe_allow_html=True)


def apply_chart_theme(figure: go.Figure) -> go.Figure:
    figure.update_layout(
        colorway=COLORWAY,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(family='Aptos, "Segoe UI", "Trebuchet MS", sans-serif', color="#172033"),
        margin=dict(l=18, r=18, t=54, b=18),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    figure.update_xaxes(showgrid=False, zeroline=False)
    figure.update_yaxes(gridcolor="rgba(23, 32, 51, 0.08)", zeroline=False)
    return figure


def format_money(value: str | Decimal | float | int) -> str:
    amount = Decimal(str(value))
    return f"${amount:,.2f}"


def outcome_tone(value: str | None) -> tuple[str, str]:
    normalized = (value or "").lower()
    if normalized in {"win", "eligible", "active"}:
        return ("Positive", "#0f766e")
    if normalized in {"no_bid", "rejected", "inactive"}:
        return ("Attention", "#dc2626")
    return ("Neutral", "#1d4ed8")
