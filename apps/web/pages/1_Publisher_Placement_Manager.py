import streamlit as st

from apps.web.api_client import api_get, api_post, require_login

current_user = require_login()

st.title("Publisher & Placement Manager")
st.caption("Manage SSP inventory in the current demo slice.")
st.write(f"Signed in as `{current_user['full_name']}` with role `{current_user['role']}`")

publishers_response = api_get("/publishers")
placements_response = api_get("/placements")

if publishers_response.status_code == 403 or placements_response.status_code == 403:
    st.error("Your role does not have permission to manage publishers and placements.")
    st.stop()

if publishers_response.status_code != 200:
    st.error("Could not load publishers from the backend.")
    st.stop()

if placements_response.status_code != 200:
    st.error("Could not load placements from the backend.")
    st.stop()

publishers = publishers_response.json()
placements = placements_response.json()

publisher_options = {publisher["name"]: publisher["id"] for publisher in publishers}

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Publishers")
    st.dataframe(publishers, use_container_width=True)

    with st.form("publisher-form"):
        publisher_name = st.text_input("Publisher name")
        publisher_status = st.selectbox("Status", ["active", "inactive"])
        publisher_submitted = st.form_submit_button("Create publisher", type="primary")
    if publisher_submitted:
        response = api_post(
            "/publishers",
            {"name": publisher_name, "status": publisher_status},
        )
        if response.status_code == 201:
            st.success("Publisher created.")
            st.rerun()
        st.error(response.json().get("detail", "Could not create publisher"))

with col_right:
    st.subheader("Placements")
    st.dataframe(placements, use_container_width=True)

    if not publisher_options:
        st.info("Create a publisher first before adding placements.")
    else:
        with st.form("placement-form"):
            selected_publisher = st.selectbox("Publisher", list(publisher_options.keys()))
            placement_name = st.text_input("Placement name")
            placement_type = st.selectbox("Placement type", ["banner", "video", "native", "interstitial"])
            placement_status = st.selectbox("Placement status", ["active", "inactive"])
            placement_submitted = st.form_submit_button("Create placement", type="primary")
        if placement_submitted:
            response = api_post(
                "/placements",
                {
                    "publisher_id": publisher_options[selected_publisher],
                    "name": placement_name,
                    "placement_type": placement_type,
                    "status": placement_status,
                },
            )
            if response.status_code == 201:
                st.success("Placement created.")
                st.rerun()
            st.error(response.json().get("detail", "Could not create placement"))
