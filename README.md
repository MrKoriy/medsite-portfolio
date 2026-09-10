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

## AI-ассистент

Плавающий чат-виджет на всех публичных страницах. Бэкенд-роутер `POST /api/assistant/chat`
строит контекст из живых данных БД (услуги, врачи, FAQ — RAG-lite) и проксирует вопрос
к LLM. Ключ хранится только на бэкенде, клиенту не отдаётся; история диалога живёт
в sessionStorage; действует rate limit (10 запросов/мин на клиента).

```bash
# включение ассистента (env при запуске uvicorn):
export AI_API_KEY='ваш-ключ-OpenAI-совместимого-провайдера'
# опционально:
export AI_BASE_URL='https://agentrouter.org/v1'   # default
export AI_MODEL='deepseek-v4-flash'               # default
```

Без `AI_API_KEY` эндпоинт отвечает `503 AI_ASSISTANT_DISABLED`, виджет показывает
вежливое сообщение — сайт остаётся полностью работоспособным.

## Тесты

```bash
cd backend
. .venv/bin/activate
pytest -v
```

Backend находится в `backend/app`, backend-тесты в `backend/tests`, статические страницы и ресурсы в `frontend`. Файл `backend/medsite.db` содержит персональные данные, включая телефоны; не публикуйте и не добавляйте его в VCS.
