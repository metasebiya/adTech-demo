from core.auth.security import hash_password, verify_password


def test_password_hash_round_trip() -> None:
    password = "ChangeMe123!"
    password_hash = hash_password(password)

    assert password_hash != password
    assert verify_password(password, password_hash) is True


def test_login_returns_access_token(client) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "admin@adtech-demo.local", "password": "ChangeMe123!"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["email"] == "admin@adtech-demo.local"


def test_login_rejects_invalid_password(client) -> None:
    response = client.post(
        "/auth/login",
        json={"email": "admin@adtech-demo.local", "password": "wrong-password"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_auth_me_requires_token(client) -> None:
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_returns_current_user(client) -> None:
    login_response = client.post(
        "/auth/login",
        json={"email": "admin@adtech-demo.local", "password": "ChangeMe123!"},
    )
    token = login_response.json()["access_token"]

    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "admin@adtech-demo.local"
    assert payload["role"] == "admin"
