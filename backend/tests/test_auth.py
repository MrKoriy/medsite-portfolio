def test_login_ok(client):
    response = client.post("/api/admin/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_login_bad_is_401(client):
    response = client.post("/api/admin/login", json={"username": "admin", "password": "wrong"})
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_CREDENTIALS"


def test_protected_endpoint_without_token_is_401(client):
    response = client.post("/api/services", json={"name": "Checkup", "price": 100, "duration_minutes": 30})
    assert response.status_code == 401
