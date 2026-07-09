def login_headers(client, email: str, password: str = "ChangeMe123!") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_overview_metrics_returns_expected_baseline(client) -> None:
    response = client.get("/metrics/overview", headers=login_headers(client, "admin@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["bid_requests"] == 1
    assert payload["wins"] == 1
    assert payload["no_bids"] == 0
    assert payload["impressions"] == 1
    assert payload["clicks"] == 1
    assert payload["conversions"] == 1
    assert payload["revenue"] == "1.25"


def test_timeseries_metrics_returns_daily_rollup(client) -> None:
    response = client.get("/metrics/timeseries", headers=login_headers(client, "analyst@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert payload[0]["bid_requests"] >= 1
    assert "date" in payload[0]


def test_campaign_metrics_returns_campaign_performance(client) -> None:
    response = client.get("/metrics/campaigns", headers=login_headers(client, "viewer@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["campaign_name"] == "Seed Campaign"
    assert payload[0]["wins"] == 1
    assert payload[0]["revenue"] == "1.25"


def test_publisher_metrics_returns_publisher_performance(client) -> None:
    response = client.get("/metrics/publishers", headers=login_headers(client, "admin@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["publisher_name"] == "Seed Publisher"
    assert payload[0]["bid_requests"] == 1
    assert payload[0]["impressions"] == 1


def test_no_bid_reason_breakdown_returns_rejections(client) -> None:
    simulate_response = client.post(
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
    assert simulate_response.status_code == 201

    response = client.get("/metrics/no-bid-reasons", headers=login_headers(client, "admin@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert any(item["reason"] == "device_mismatch" for item in payload)


def test_viewer_can_access_dashboard_metrics(client) -> None:
    response = client.get("/metrics/overview", headers=login_headers(client, "viewer@adtech-demo.local"))

    assert response.status_code == 200
