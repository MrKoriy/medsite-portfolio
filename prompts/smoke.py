"""Живой smoke-тест мед-сайта: запись, дубль слота, админка, маскирование."""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"

def req(method: str, path: str, body: dict | None = None, token: str | None = None) -> tuple[int, dict | str]:
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(r, timeout=15) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)

# 1. health
code, health = req("GET", "/api/health")
print(f"HEALTH          {code} {health}")

# 2. admin login
code, login = req("POST", "/api/admin/login", {"username": "smokeadmin", "password": "SmokePass123!"})
token = login["token"] if isinstance(login, dict) else ""
print(f"LOGIN           {code} token={token[:10]}...")

# 3. дубль-бронь: слот 09:00 2026-09-12 занят? создадим запись, затем повторим
BODY = {
    "doctor_id": 1, "service_id": 1, "slot_start": "2026-09-12T09:00:00",
    "client_name": "Анна Петрова", "client_phone": "+79990001234",
    "utm_source": "telegram", "utm_campaign": "portfolio",
    "source": "website", "client_id": "cid-test-001",
}
code, created = req("POST", "/api/appointments", BODY)
print(f"CREATE          {code} {json.dumps(created, ensure_ascii=False)[:300]}")
code, dup = req("POST", "/api/appointments", BODY)
print(f"DUPLICATE       {code} {json.dumps(dup, ensure_ascii=False)[:160]}")

# 4. админ-список new
code, items = req("GET", "/api/admin/appointments?status=new", token=token)
print(f"ADMIN_LIST      {code} items={len(items.get('items', [])) if isinstance(items, dict) else '?'}")
appt_id = created["id"] if isinstance(created, dict) and "id" in created else None

# 5. смена статуса
if appt_id:
    code, patched = req("PATCH", f"/api/admin/appointments/{appt_id}", {"status": "confirmed"}, token)
    print(f"PATCH_STATUS    {code} status={patched.get('status') if isinstance(patched, dict) else '?'}")

# 6. админ без токена
code, unauth = req("GET", "/api/admin/appointments")
print(f"UNAUTH          {code} {json.dumps(unauth, ensure_ascii=False)[:120]}")

# 7. публичные списки (телефоны не утекают?)
code, doctors = req("GET", "/api/doctors")
s = json.dumps(doctors, ensure_ascii=False)
print(f"DOCTORS_PUBLIC  {code} phone_leak={'79990001234' in s}")
code, appts = req("GET", "/api/admin/appointments", token=token)
s2 = json.dumps(appts, ensure_ascii=False)
print(f"ADMIN_APPTS     {code} full_phone_visible={'79990001234' in s2}")
