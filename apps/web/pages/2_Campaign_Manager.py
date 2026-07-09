import streamlit as st

from apps.web.api_client import api_get, api_patch, api_post, require_login

current_user = require_login()

st.title("Campaign Manager")
st.caption("Create, inspect, and update campaigns for the SSP demo workflow.")
st.write(f"Signed in as `{current_user['full_name']}` with role `{current_user['role']}`")

campaigns_response = api_get("/campaigns")
placements_response = api_get("/placements")

if campaigns_response.status_code == 403 or placements_response.status_code == 403:
    st.error("Your role does not have permission to manage campaigns.")
    st.stop()

if campaigns_response.status_code != 200:
    st.error("Could not load campaigns from the backend.")
    st.stop()

if placements_response.status_code != 200:
    st.error("Could not load placements from the backend.")
    st.stop()

campaigns = campaigns_response.json()
placements = placements_response.json()
placement_options = {
    f"{placement['name']} (#{placement['id']})": placement["id"]
    for placement in placements
}

st.subheader("Existing Campaigns")
st.dataframe(campaigns, use_container_width=True)

create_col, update_col = st.columns(2)

with create_col:
    st.subheader("Create Campaign")
    with st.form("campaign-create-form"):
        campaign_name = st.text_input("Campaign name")
        advertiser_name = st.text_input("Advertiser name")
        campaign_status = st.selectbox("Status", ["draft", "active", "inactive"])
        bid_cpm = st.number_input("Bid CPM", min_value=0.01, value=2.50, step=0.25)
        daily_budget = st.number_input("Daily budget", min_value=0.01, value=100.00, step=10.0)
        remaining_budget = st.number_input("Remaining budget", min_value=0.0, value=100.00, step=10.0)
        frequency_cap = st.number_input("Frequency cap", min_value=1, value=3, step=1)
        target_country = st.text_input("Target country", value="US")
        target_device = st.selectbox("Target device", ["desktop", "mobile", "tablet", "ctv"])
        target_placement = st.selectbox("Target placement", list(placement_options.keys()))
        create_submitted = st.form_submit_button("Create campaign", type="primary")
    if create_submitted:
        response = api_post(
            "/campaigns",
            {
                "name": campaign_name,
                "advertiser_name": advertiser_name,
                "status": campaign_status,
                "bid_cpm": str(bid_cpm),
                "daily_budget": str(daily_budget),
                "remaining_budget": str(remaining_budget),
                "frequency_cap": int(frequency_cap),
                "targets": [
                    {
                        "country": target_country,
                        "device_type": target_device,
                        "placement_id": placement_options[target_placement],
                    }
                ],
            },
        )
        if response.status_code == 201:
            st.success("Campaign created.")
            st.rerun()
        st.error(response.json().get("detail", "Could not create campaign"))

with update_col:
    st.subheader("Update Campaign Status")
    if not campaigns:
        st.info("No campaigns available yet.")
    else:
        campaign_index = {
            f"{campaign['name']} (#{campaign['id']})": campaign["id"]
            for campaign in campaigns
        }
        with st.form("campaign-update-form"):
            selected_campaign = st.selectbox("Campaign", list(campaign_index.keys()))
            updated_status = st.selectbox("New status", ["draft", "active", "inactive"])
            update_submitted = st.form_submit_button("Update status", type="primary")
        if update_submitted:
            response = api_patch(
                f"/campaigns/{campaign_index[selected_campaign]}",
                {"status": updated_status},
            )
            if response.status_code == 200:
                st.success("Campaign updated.")
                st.rerun()
            st.error(response.json().get("detail", "Could not update campaign"))
