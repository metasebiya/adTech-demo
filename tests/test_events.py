def login_headers(client, email: str, password: str = "ChangeMe123!") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_can_create_impression_event(client) -> None:
    response = client.post(
        "/events/impression",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "auction_decision_id": 1,
            "campaign_id": 1,
            "publisher_id": 1,
            "placement_id": 1,
            "user_id": "existing-user",
            "revenue": "2.15",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["auction_decision_id"] == 1
    assert payload["revenue"] == "2.15"


def test_adops_can_create_click_and_conversion_events(client) -> None:
    click_response = client.post(
        "/events/click",
        headers=login_headers(client, "adops@adtech-demo.local"),
        json={"auction_decision_id": 1, "campaign_id": 1},
    )
    conversion_response = client.post(
        "/events/conversion",
        headers=login_headers(client, "adops@adtech-demo.local"),
        json={"auction_decision_id": 1, "campaign_id": 1, "conversion_value": "12.50"},
    )

    assert click_response.status_code == 201
    assert conversion_response.status_code == 201
    assert conversion_response.json()["conversion_value"] == "12.50"


def test_event_creation_rejects_non_winning_campaign_reference(client) -> None:
    response = client.post(
        "/events/click",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={"auction_decision_id": 1, "campaign_id": 999},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Event must reference the winning campaign for a winning auction"


def test_event_creation_rejects_inventory_mismatch_for_impression(client) -> None:
    response = client.post(
        "/events/impression",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "auction_decision_id": 1,
            "campaign_id": 1,
            "publisher_id": 1,
            "placement_id": 999,
            "user_id": "fresh-user",
            "revenue": "0.50",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Impression inventory does not match auction decision"


def test_event_creation_rejects_user_mismatch_for_impression(client) -> None:
    response = client.post(
        "/events/impression",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "auction_decision_id": 1,
            "campaign_id": 1,
            "publisher_id": 1,
            "placement_id": 1,
            "user_id": "someone-else",
            "revenue": "0.50",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Impression user does not match auction decision"


def test_analyst_can_list_events(client) -> None:
    response = client.get("/events", headers=login_headers(client, "analyst@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    event_types = {item["event_type"] for item in payload}
    assert {"impression", "click", "conversion"}.issubset(event_types)


def test_viewer_cannot_list_events(client) -> None:
    response = client.get("/events", headers=login_headers(client, "viewer@adtech-demo.local"))

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to perform this action"


def test_events_can_be_filtered_by_campaign_and_auction(client) -> None:
    response = client.get(
        "/events",
        headers=login_headers(client, "admin@adtech-demo.local"),
        params={"campaign_id": 1, "auction_decision_id": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 3
    assert all(item["campaign_id"] == 1 for item in payload)
    assert all(item["auction_decision_id"] == 1 for item in payload)


def test_events_can_be_filtered_by_publisher(client) -> None:
    response = client.get(
        "/events",
        headers=login_headers(client, "admin@adtech-demo.local"),
        params={"publisher_id": 999},
    )

    assert response.status_code == 200
    assert response.json() == []
