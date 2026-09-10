def service_payload(name="Consultation"):
    return {"name": name, "description": "Visit", "price": 2500, "duration_minutes": 30, "is_active": True}


def test_services_crud(client, auth_headers):
    created = client.post("/api/services", json=service_payload(), headers=auth_headers)
    assert created.status_code == 201
    service_id = created.json()["id"]
    assert client.get("/api/services").json()["items"][0]["name"] == "Consultation"
    updated = client.put(f"/api/services/{service_id}", json=service_payload("Follow-up"), headers=auth_headers)
    assert updated.status_code == 200
    assert client.delete(f"/api/services/{service_id}", headers=auth_headers).status_code == 204


def test_doctors_crud_and_service_link(client, auth_headers):
    service = client.post("/api/services", json=service_payload(), headers=auth_headers).json()
    payload = {"full_name": "Ivan Petrov", "specialty": "Cardiologist", "service_ids": [service["id"]]}
    created = client.post("/api/doctors", json=payload, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["service_ids"] == [service["id"]]
    assert client.get("/api/doctors").json()["items"][0]["full_name"] == "Ivan Petrov"
    assert client.put(f"/api/doctors/{created.json()['id']}", json=payload, headers=auth_headers).status_code == 200


def test_faq_crud(client, auth_headers):
    payload = {"question": "How?", "answer": "Carefully", "sort_order": 1, "is_active": True}
    created = client.post("/api/faq", json=payload, headers=auth_headers)
    assert created.status_code == 201
    faq_id = created.json()["id"]
    assert client.get("/api/faq").json()["items"][0]["question"] == "How?"
    assert client.put(f"/api/faq/{faq_id}", json=payload, headers=auth_headers).status_code == 200
    assert client.delete(f"/api/faq/{faq_id}", headers=auth_headers).status_code == 204
