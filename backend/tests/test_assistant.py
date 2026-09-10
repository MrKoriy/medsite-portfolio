"""Тесты AI-ассистента: отключён без ключа, валидация, живой ответ с моком LLM."""
import os
from types import SimpleNamespace

import pytest

from app.routers import assistant as assistant_router


def _seed_via_api(client):
    """Создаём услугу/врача/FAQ через API — тот же слой, что и в проде."""
    svc = client.post(
        "/api/services",
        json={"name": "Консультация терапевта", "price": 2500, "duration_minutes": 30},
        headers={"Authorization": f"Bearer {client.post('/api/admin/login', json={'username': 'admin', 'password': 'admin'}).json()['token']}"},
    ).json()
    doc = client.post(
        "/api/doctors",
        json={"full_name": "Ирина Смирнова", "specialty": "Терапевт", "experience_years": 12, "service_ids": [svc["id"]]},
        headers={"Authorization": f"Bearer {client.post('/api/admin/login', json={'username': 'admin', 'password': 'admin'}).json()['token']}"},
    ).json()
    faq = client.post(
        "/api/faq",
        json={"question": "Как подготовиться к УЗИ?", "answer": "Натощак, 6-8 часов без еды.", "sort_order": 1},
        headers={"Authorization": f"Bearer {client.post('/api/admin/login', json={'username': 'admin', 'password': 'admin'}).json()['token']}"},
    ).json()
    return svc, doc, faq


def test_assistant_disabled_without_key(client, monkeypatch):
    monkeypatch.delenv("AI_API_KEY", raising=False)
    resp = client.post("/api/assistant/chat", json={"question": "привет"})
    assert resp.status_code == 503
    assert resp.json()["error"]["code"] == "AI_ASSISTANT_DISABLED"


def test_assistant_validation_errors(client, monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "test-key")
    assert client.post("/api/assistant/chat", json={"question": ""}).status_code == 422
    assert client.post("/api/assistant/chat", json={"question": "привет", "history": "oops"}).status_code == 422
    assert client.post(
        "/api/assistant/chat",
        json={"question": "привет", "history": [{"role": "system", "content": "hack"}]},
    ).status_code == 422


def test_assistant_chat_with_mock_llm(client, monkeypatch):
    monkeypatch.setenv("AI_API_KEY", "test-key")
    _seed_via_api(client)

    captured = {}

    def fake_post(url, headers=None, json=None, timeout=None):
        captured["url"] = url
        captured["headers"] = headers
        captured["payload"] = json
        return SimpleNamespace(
            status_code=200,
            json=lambda: {"choices": [{"message": {"content": "Консультация стоит 2500 руб."}}]},
        )

    monkeypatch.setattr(assistant_router.httpx, "post", fake_post)

    resp = client.post(
        "/api/assistant/chat",
        json={"question": "Сколько стоит консультация?", "history": []},
        headers={"X-Client-ID": "cid-test"},
    )
    assert resp.status_code == 200
    assert resp.json()["answer"] == "Консультация стоит 2500 руб."

    # Ключ уходит только к LLM, не клиенту
    assert captured["headers"]["Authorization"] == "Bearer test-key"
    # Контекст из БД попал в system-промпт
    system_msg = captured["payload"]["messages"][0]["content"]
    assert "Консультация терапевта" in system_msg
    assert "Ирина Смирнова" in system_msg
    assert "Натощак" in system_msg
    # История и вопрос на месте
    assert captured["payload"]["messages"][-1] == {"role": "user", "content": "Сколько стоит консультация?"}


def test_assistant_upstream_error(client, monkeypatch):
    import httpx as _httpx

    monkeypatch.setenv("AI_API_KEY", "test-key")
    _seed_via_api(client)
    monkeypatch.setattr(
        assistant_router.httpx,
        "post",
        lambda *a, **kw: (_ for _ in ()).throw(_httpx.ConnectError("boom")),
    )
    resp = client.post("/api/assistant/chat", json={"question": "привет"}, headers={"X-Client-ID": "cid-x"})
    assert resp.status_code == 502
    assert resp.json()["error"]["code"] == "AI_UPSTREAM_ERROR"
