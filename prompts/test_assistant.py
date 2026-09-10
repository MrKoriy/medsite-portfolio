"""E2E-тест AI-ассистента: сервисы -> вопрос -> ответ с данными из БД."""
import json
import time
import urllib.request
import urllib.error

BASE = "http://127.0.0.1:8000"


def req(method: str, path: str, body: dict | None = None, token: str | None = None, client: str = "test-cid-1"):
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


# Ждём подъёма сервера
for _ in range(40):
    try:
        code, health = req("GET", "/api/health", client="")
        if code == 200:
            break
    except Exception:
        pass
    time.sleep(0.5)
print(f"HEALTH           {code} {health}")

# Логин и наполнение данными
code, login = req("POST", "/api/admin/login", {"username": "smokeadmin", "password": "SmokePass123!"}, client="")
token = login["token"]

svc1 = req("POST", "/api/services", {"name": "Консультация терапевта", "price": 2500, "duration_minutes": 30}, token)[1]
svc2 = req("POST", "/api/services", {"name": "УЗИ брюшной полости", "price": 3800, "duration_minutes": 45,
                                     "description": "Ультразвуковое исследование органов брюшной полости"}, token)[1]
print(f"SERVICES         созданы: id={svc1['id']}, id={svc2['id']}")

doc = req("POST", "/api/doctors", {"full_name": "Ирина Смирнова", "specialty": "Терапевт",
                                   "experience_years": 12, "service_ids": [svc1["id"]], "bio": "Ведёт терапию и профилактику"}, token)[1]
req("POST", "/api/doctors", {"full_name": "Павел Котов", "specialty": "УЗИ-диагностика",
                             "experience_years": 8, "service_ids": [svc2["id"]], "bio": "Специалист по УЗИ"}, token)
print(f"DOCTOR           создан: {doc['full_name']}")

faq = req("POST", "/api/faq", {"question": "Нужна ли подготовка к УЗИ?", "answer": "Приходите натощак, не ешьте 6-8 часов до исследования.", "sort_order": 1}, token)[1]
print(f"FAQ              создан: id={faq['id']}")

# Вопросы ассистенту
questions = [
    "Сколько стоит консультация терапевта и кто ведёт приём?",
    "Как подготовиться к УЗИ брюшной полости?",
    "Во сколько вы работаете и как записаться?",
]
history = []
for q in questions:
    code, ans = req("POST", "/api/assistant/chat", {"question": q, "history": history})
    if code == 200 and isinstance(ans, dict):
        a = ans["answer"]
        print(f"\nQ: {q}\nA ({code}): {a}")
        history = (history + [{"role": "user", "content": q}, {"role": "assistant", "content": a}])[-12:]
    else:
        print(f"\nQ: {q}\nERR ({code}): {json.dumps(ans, ensure_ascii=False)[:200]}")

# Проверка ошибок: пустой вопрос, отключённый ассистент
code, err = req("POST", "/api/assistant/chat", {"question": "", "history": []})
print(f"\nEMPTY_Q          {code} (ожидание 422)")
code, err = req("POST", "/api/assistant/chat", {"question": "привет", "history": "not-a-list"})
print(f"BAD_HISTORY      {code} (ожидание 422)")
