# Medsite

Портфолио-прототип медицинского сайта: FastAPI + SQLite API и статический HTML/CSS/JS frontend.

## Запуск

```bash
cd backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD='replace-with-a-strong-password'
export CORS_ORIGINS=http://127.0.0.1:8080
uvicorn app.main:app --reload --port 8000
```

В другом терминале:

```bash
cd frontend
python3 -m http.server 8080
```

Откройте `http://127.0.0.1:8080`. URL API задаётся только в `frontend/js/config.js`.

## Тесты

```bash
cd backend
. .venv/bin/activate
pytest -v
```

Backend находится в `backend/app`, backend-тесты в `backend/tests`, статические страницы и ресурсы в `frontend`. Файл `backend/medsite.db` содержит персональные данные, включая телефоны; не публикуйте и не добавляйте его в VCS.
