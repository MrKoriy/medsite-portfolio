from datetime import datetime, timedelta


def setup_booking(client, headers):
    service = client.post("/api/services", json={"name": "Consultation", "price": 2500, "duration_minutes": 30}, headers=headers).json()
    doctor = client.post("/api/doctors", json={"full_name": "Ivan Petrov", "specialty": "Cardiologist", "service_ids": [service["id"]]}, headers=headers).json()
    slot = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    return service, doctor, slot


def test_slots_creation_and_busy_slot_conflict(client, auth_headers):
    service, doctor, slot = setup_booking(client, auth_headers)
    date = slot.date().isoformat()
    slots = client.get(f"/api/doctors/{doctor['id']}/slots", params={"date": date}).json()["slots"]
    assert slot.isoformat(timespec="seconds") in slots
    payload = {"doctor_id": doctor["id"], "service_id": service["id"], "slot_start": slot.isoformat(timespec="seconds"), "client_name": "Anna", "client_phone": "+79990000000", "utm_source": "google", "client_id": "cid"}
    created = client.post("/api/appointments", json=payload)
    assert created.status_code == 201
    assert created.json()["lead_id"]
    assert slot.isoformat(timespec="seconds") not in client.get(f"/api/doctors/{doctor['id']}/slots", params={"date": date}).json()["slots"]
    assert client.post("/api/appointments", json=payload).status_code == 409


def test_appointment_status_change_and_admin_listing(client, auth_headers):
    service, doctor, slot = setup_booking(client, auth_headers)
    payload = {"doctor_id": doctor["id"], "service_id": service["id"], "slot_start": slot.isoformat(timespec="seconds"), "client_name": "Anna", "client_phone": "+79990000000"}
    appointment = client.post("/api/appointments", json=payload).json()
    response = client.patch(f"/api/admin/appointments/{appointment['id']}", json={"status": "confirmed"}, headers=auth_headers)
    assert response.status_code == 200
    assert client.get("/api/admin/appointments?status=confirmed", headers=auth_headers).json()["items"][0]["status"] == "confirmed"


def test_long_appointment_hides_all_overlapping_slots(client, auth_headers):
    service = client.post("/api/services", json={"name": "Long visit", "price": 3000, "duration_minutes": 60}, headers=auth_headers).json()
    doctor = client.post("/api/doctors", json={"full_name": "Long Visit Doctor", "specialty": "Therapist", "service_ids": [service["id"]]}, headers=auth_headers).json()
    slot = (datetime.now() + timedelta(days=2)).replace(hour=10, minute=0, second=0, microsecond=0)
    payload = {"doctor_id": doctor["id"], "service_id": service["id"], "slot_start": slot.isoformat(timespec="seconds"), "client_name": "Anna", "client_phone": "+79990000000"}
    assert client.post("/api/appointments", json=payload).status_code == 201
    slots = client.get(f"/api/doctors/{doctor['id']}/slots", params={"date": slot.date().isoformat()}).json()["slots"]
    assert slot.isoformat(timespec="seconds") not in slots
    assert (slot + timedelta(minutes=30)).isoformat(timespec="seconds") not in slots


def test_slot_that_does_not_fit_workday_is_validation_error(client, auth_headers):
    service, doctor, slot = setup_booking(client, auth_headers)
    slot = slot.replace(hour=17, minute=45)
    payload = {"doctor_id": doctor["id"], "service_id": service["id"], "slot_start": slot.isoformat(timespec="seconds"), "client_name": "Anna", "client_phone": "+79990000000"}
    response = client.post("/api/appointments", json=payload)
    assert response.status_code == 422
