def login_headers(client, email: str, password: str = "ChangeMe123!") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_admin_can_list_campaigns(client) -> None:
    response = client.get("/campaigns", headers=login_headers(client, "admin@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Seed Campaign"
    assert payload[0]["targets"][0]["country"] == "US"


def test_adops_can_create_campaign(client) -> None:
    response = client.post(
        "/campaigns",
        headers=login_headers(client, "adops@adtech-demo.local"),
        json={
            "name": "Video Burst Campaign",
            "advertiser_name": "Contoso",
            "status": "active",
            "bid_cpm": "3.75",
            "daily_budget": "300.00",
            "remaining_budget": "250.00",
            "frequency_cap": 4,
            "targets": [
                {
                    "country": "ke",
                    "device_type": "mobile",
                    "placement_id": 1,
                }
            ],
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Video Burst Campaign"
    assert payload["created_by_user_id"] > 0
    assert payload["targets"][0]["country"] == "KE"


def test_analyst_cannot_list_campaigns(client) -> None:
    response = client.get("/campaigns", headers=login_headers(client, "analyst@adtech-demo.local"))

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to perform this action"


def test_get_campaign_returns_single_campaign(client) -> None:
    response = client.get("/campaigns/1", headers=login_headers(client, "admin@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 1
    assert payload["advertiser_name"] == "Seed Advertiser"


def test_patch_campaign_updates_status_and_targets(client) -> None:
    response = client.patch(
        "/campaigns/1",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "status": "inactive",
            "targets": [
                {
                    "country": "ca",
                    "device_type": "tablet",
                    "placement_id": 1,
                }
            ],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "inactive"
    assert payload["targets"][0]["country"] == "CA"
    assert payload["targets"][0]["device_type"] == "tablet"


def test_create_campaign_rejects_missing_placement(client) -> None:
    response = client.post(
        "/campaigns",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "name": "Broken Campaign",
            "advertiser_name": "Unknown",
            "status": "draft",
            "bid_cpm": "1.20",
            "daily_budget": "50.00",
            "remaining_budget": "20.00",
            "frequency_cap": 2,
            "targets": [
                {
                    "country": "US",
                    "device_type": "desktop",
                    "placement_id": 999,
                }
            ],
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Placement ids not found: 999"


def test_create_campaign_rejects_invalid_budget(client) -> None:
    response = client.post(
        "/campaigns",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "name": "Overbudget Campaign",
            "advertiser_name": "Budget Co",
            "status": "active",
            "bid_cpm": "2.10",
            "daily_budget": "60.00",
            "remaining_budget": "75.00",
            "frequency_cap": 2,
            "targets": [
                {
                    "country": "US",
                    "device_type": "desktop",
                    "placement_id": 1,
                }
            ],
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Remaining budget cannot exceed daily budget"
