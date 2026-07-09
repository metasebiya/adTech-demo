def login_headers(client, email: str, password: str = "ChangeMe123!") -> dict[str, str]:
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_analyst_can_get_suggested_questions(client) -> None:
    response = client.get("/copilot/suggested-questions", headers=login_headers(client, "analyst@adtech-demo.local"))

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 4
    assert any(item["category"] == "analytics" for item in payload)


def test_viewer_cannot_use_copilot(client) -> None:
    response = client.get("/copilot/suggested-questions", headers=login_headers(client, "viewer@adtech-demo.local"))

    assert response.status_code == 403


def test_copilot_explains_specific_auction(client) -> None:
    response = client.post(
        "/copilot/query",
        headers=login_headers(client, "admin@adtech-demo.local"),
        json={"query": "Why did auction 1 select its winner?"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "auction_explanation"
    assert "Auction 1" in payload["title"]
    assert "winning" in payload["answer"].lower() or "win" in payload["answer"].lower()
    assert "auction_decisions" in payload["inspected_sources"]


def test_copilot_summarizes_marketplace_analytics(client) -> None:
    response = client.post(
        "/copilot/query",
        headers=login_headers(client, "adops@adtech-demo.local"),
        json={"query": "Summarize current performance across the marketplace"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "analytics_summary"
    assert "win rate" in payload["answer"].lower()
    assert "metrics.overview" in payload["inspected_sources"]
