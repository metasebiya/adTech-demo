def login_headers(client, email: str, password: str = "ChangeMe123!") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_bid_request_returns_winning_campaign(client) -> None:
    response = client.post(
        "/bid-requests",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "publisher_id": 1,
            "placement_id": 1,
            "country": "US",
            "device_type": "desktop",
            "user_id": "fresh-user",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["auction_decision"]["decision_status"] == "win"
    assert payload["auction_decision"]["winner_campaign_id"] == 1
    assert payload["auction_decision"]["clearing_price"] == "2.50"


def test_bid_request_returns_no_bid_for_device_mismatch(client) -> None:
    response = client.post(
        "/bid-requests",
        headers=login_headers(client, "adops@adtech-demo.local"),
        json={
            "publisher_id": 1,
            "placement_id": 1,
            "country": "US",
            "device_type": "mobile",
            "user_id": "fresh-user",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["auction_decision"]["decision_status"] == "no_bid"
    assert payload["auction_decision"]["decision_reason"] == "no_eligible_campaign"
    candidate = payload["auction_decision"]["candidates"][0]
    assert candidate["eligibility_status"] == "rejected"
    assert candidate["rejection_reason"] == "device_mismatch"


def test_bid_request_rejects_frequency_cap_reached(client) -> None:
    response = client.post(
        "/bid-requests",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "publisher_id": 1,
            "placement_id": 1,
            "country": "US",
            "device_type": "desktop",
            "user_id": "existing-user",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["auction_decision"]["decision_status"] == "no_bid"
    candidate = payload["auction_decision"]["candidates"][0]
    assert candidate["rejection_reason"] == "frequency_cap_reached"


def test_analyst_can_list_auctions(client) -> None:
    response = client.get("/auctions", headers=login_headers(client, "analyst@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert payload[0]["decision_status"] in {"win", "no_bid"}


def test_viewer_can_get_single_auction(client) -> None:
    response = client.get("/auctions/1", headers=login_headers(client, "viewer@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["winner_campaign_id"] == 1


def test_viewer_cannot_run_bid_simulation(client) -> None:
    response = client.post(
        "/bid-requests",
        headers=login_headers(client, "viewer@adtech-demo.local"),
        json={
            "publisher_id": 1,
            "placement_id": 1,
            "country": "US",
            "device_type": "desktop",
            "user_id": "blocked-user",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to perform this action"
