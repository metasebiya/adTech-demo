import streamlit as st
import requests

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
    "This first slice only includes authentication. Dashboard, campaigns, placements, auctions, and analytics come next."
)
