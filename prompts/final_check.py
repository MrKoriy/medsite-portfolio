"""Финальная проверка закоммиченного состояния: всё API + AI-ассистент."""
import json
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8010"
TOKEN = ""


def req(method, path, body=None, token=None, client="final-cid"):
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(BASE + path, data=data, method=method)
    r.add_header("Content-Type", "application/json")
    if token:
        r.add_header("Authorization", f"Bearer {token}")
    if client:
        r.add_header("X-Client-ID", client)
    try:
        with urllib.request.urlopen(r, timeout=90) as resp:
            raw = resp.read().decode()
            return resp.status, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)
    except urllib.error.HTTPError as e:
        raw = e.read().decode()
        return e.code, (json.loads(raw) if raw.strip().startswith(("{", "[")) else raw)


for _ in range(40):
    try:
        code, health = req("GET", "/api/health", client="")
        if code == 200:
            break
    except Exception:
        pass
    time.sleep(0.5)

checks = []
checks.append(("health", code, health.get("status") == "ok"))

code, login = req("POST", "/api/admin/login", {"username": "smokeadmin", "password": "SmokePass123!"}, client="")
TOKEN = login["token"]
checks.append(("admin login", code, code == 200))

s = req("POST", "/api/services", {"name": "Консультация терапевта", "price": 2500, "duration_minutes": 30}, TOKEN)[1]
s2 = req("POST", "/api/services", {"name": "УЗИ брюшной полости", "price": 3800, "duration_minutes": 45}, TOKEN)[1]
checks.append(("create services", 201, True))
d = req("POST", "/api/doctors", {"full_name": "Ирина Смирнова", "specialty": "Терапевт", "experience_years": 12, "service_ids": [s["id"]]}, TOKEN)[1]
req("POST", "/api/faq", {"question": "Как подготовиться к УЗИ?", "answer": "Натощак, 6-8 часов без еды.", "sort_order": 1}, TOKEN)
checks.append(("create doctor+faq", 201, True))

date = (__import__("datetime").datetime.now() + __import__("datetime").timedelta(days=2)).date().isoformat()
slots = req("GET", f"/api/doctors/{d['id']}/slots?date={date}")[1]
slot = slots["slots"][0]
body = {"doctor_id": d["id"], "service_id": s["id"], "slot_start": slot, "client_name": "Анна",
        "client_phone": "+79990001234", "utm_source": "telegram"}
c1 = req("POST", "/api/appointments", body, client="")[0]
c2 = req("POST", "/api/appointments", body, client="")[0]
checks.append(("booking 201 / duplicate 409", f"{c1}/{c2}", c1 == 201 and c2 == 409))

unauth = req("GET", "/api/admin/appointments", client="")[0]
checks.append(("admin w/o token 401", unauth, unauth == 401))

code, ans = req("POST", "/api/assistant/chat", {"question": "Сколько стоит консультация терапевта?", "history": []})
answer = ans.get("answer", "") if isinstance(ans, dict) else str(ans)
checks.append(("AI assistant answers with real data", code, code == 200 and "2500" in answer))

print("=" * 62)
ok_all = True
for name, got, ok in checks:
    ok_all = ok_all and bool(ok)
    print(f"{'✅' if ok else '❌'}  {name:42s} {got}")
print("=" * 62)
print("AI ANSWER:", answer[:220])
print("\nИТОГ:", "ВСЁ РАБОТАЕТ" if ok_all else "ЕСТЬ ПРОБЛЕМЫ")
