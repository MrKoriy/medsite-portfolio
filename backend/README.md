# Backend

FastAPI + SQLAlchemy 2.0 + SQLite REST API по контракту `PLAN.md`.

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Администратор создаётся при первом запуске из обязательных `ADMIN_USERNAME` и `ADMIN_PASSWORD`. Для другой БД можно задать `DATABASE_URL`; CORS настраивается явным списком origins через `CORS_ORIGINS`.

`medsite.db` содержит персональные данные, включая телефоны заявителей. Не публикуйте и не добавляйте этот файл в VCS.
