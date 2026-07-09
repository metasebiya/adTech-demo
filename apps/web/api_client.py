from typing import Any

import requests
import streamlit as st

from core.config import get_settings

settings = get_settings()


def get_auth_headers() -> dict[str, str]:
    token = st.session_state.get("access_token")
    if not token:
        return {}
    return {"Authorization": f"Bearer {token}"}


def api_get(path: str, params: dict[str, Any] | None = None) -> requests.Response:
    return requests.get(
        f"{settings.api_base_url}{path}",
        headers=get_auth_headers(),
        params=params,
        timeout=10,
    )


def api_post(path: str, payload: dict[str, Any]) -> requests.Response:
    return requests.post(
        f"{settings.api_base_url}{path}",
        headers=get_auth_headers(),
        json=payload,
        timeout=10,
    )


def api_patch(path: str, payload: dict[str, Any]) -> requests.Response:
    return requests.patch(
        f"{settings.api_base_url}{path}",
        headers=get_auth_headers(),
        json=payload,
        timeout=10,
    )


def require_login() -> dict[str, Any] | None:
    current_user = st.session_state.get("current_user")
    token = st.session_state.get("access_token")
    if current_user and token:
        return current_user
    st.warning("Please sign in on the main login page first.")
    st.stop()
