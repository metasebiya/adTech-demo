def login_headers(client, email: str, password: str = "ChangeMe123!") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_list_publishers(client) -> None:
    response = client.get("/publishers", headers=login_headers(client, "admin@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Seed Publisher"


def test_adops_can_create_publisher(client) -> None:
    response = client.post(
        "/publishers",
        headers=login_headers(client, "adops@adtech-demo.local"),
        json={"name": "Mobile Apps Group", "status": "active"},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Mobile Apps Group"
    assert payload["status"] == "active"


def test_duplicate_publisher_name_returns_conflict(client) -> None:
    response = client.post(
        "/publishers",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={"name": "Seed Publisher", "status": "active"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Publisher name already exists"


def test_analyst_cannot_manage_publishers(client) -> None:
    response = client.get("/publishers", headers=login_headers(client, "analyst@adtech-demo.local"))

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to perform this action"


def test_viewer_cannot_manage_placements(client) -> None:
    response = client.get("/placements", headers=login_headers(client, "viewer@adtech-demo.local"))

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not have permission to perform this action"


def test_admin_can_create_placement(client) -> None:
    response = client.post(
        "/placements",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "publisher_id": 1,
            "name": "Sidebar Native Card",
            "placement_type": "native",
            "status": "active",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["publisher_id"] == 1
    assert payload["placement_type"] == "native"


def test_create_placement_requires_existing_publisher(client) -> None:
    response = client.post(
        "/placements",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={
            "publisher_id": 999,
            "name": "Unknown Placement",
            "placement_type": "banner",
            "status": "active",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Publisher not found"
