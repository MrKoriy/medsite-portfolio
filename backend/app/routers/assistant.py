"""AI-ассистент клиники: RAG-lite по данным БД + прокси к LLM.

Ключ LLM хранится ТОЛЬКО на бэкенде (env AI_API_KEY; опционально AI_BASE_URL,
AI_MODEL). Клиенту он не отдаётся никогда. История диалога живёт в
sessionStorage клиента и передаётся ограниченным списком сообщений.
"""
import os
import time
from collections import defaultdict, deque

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select

from ..database import get_db
from ..models import Doctor, Faq, Service

router = APIRouter(prefix="/assistant", tags=["assistant"])

AI_BASE_URL = os.getenv("AI_BASE_URL", "https://agentrouter.org/v1").rstrip("/")
AI_MODEL = os.getenv("AI_MODEL", "deepseek-v4-flash")
HTTP_TIMEOUT_SECONDS = 45.0
MAX_QUESTION_CHARS = 800
MAX_HISTORY_MESSAGES = 12
RATE_LIMIT_PER_MINUTE = 10
AGENTROUTER_USER_AGENT = "Cline/3.0.0"

SYSTEM_PROMPT = (
    "Ты — вежливый ассистент медицинской клиники «МедСфера». "
    "Отвечай кратко, по-русски, дружелюбно и только на темы клиники: услуги, "
    "врачи, цены, запись, часы работы. Не ставь диагнозы и не давай медицинских "
    "рекомендаций — мягко предлагай записаться к врачу. Если данных нет в "
    "контексте — честно скажи и предложи оставить заявку через форму на сайте. "
    "Отвечай в 2-4 предложениях."
)

# Per-process in-memory rate limit (для прототипа достаточно)
_RATE_BUCKETS: dict[str, deque] = defaultdict(lambda: deque(maxlen=RATE_LIMIT_PER_MINUTE * 2))


def _rate_limited(client_key: str) -> bool:
    bucket = _RATE_BUCKETS[client_key]
    now = time.monotonic()
    bucket.append(now)
    recent = sum(1 for ts in bucket if now - ts < 60.0)
    return recent > RATE_LIMIT_PER_MINUTE


def _build_clinic_context(db) -> str:
    """RAG-lite: свежий срез услуг/врачей/FAQ прямо из БД."""
    parts: list[str] = []

    services = db.scalars(
        select(Service).where(Service.is_active.is_(True)).order_by(Service.name)
    ).all()
    if services:
        lines = [
            f"- {s.name}: {s.price} руб., {s.duration_minutes} мин."
            + (f" {s.description[:120]}" if s.description else "")
            for s in services[:20]
        ]
        parts.append("УСЛУГИ:\n" + "\n".join(lines))

    doctors = db.scalars(
        select(Doctor).where(Doctor.is_active.is_(True)).order_by(Doctor.full_name)
    ).all()
    if doctors:
        lines = []
        for d in doctors[:20]:
            svc = ", ".join(s.name for s in d.services) or "без привязанных услуг"
            lines.append(
                f"- {d.full_name}, {d.specialty}, опыт {d.experience_years} лет; услуги: {svc}"
            )
        parts.append("ВРАЧИ:\n" + "\n".join(lines))

    faq = db.scalars(
        select(Faq).where(Faq.is_active.is_(True)).order_by(Faq.sort_order)
    ).all()
    if faq:
        lines = [f"- Q: {f.question} A: {f.answer[:200]}" for f in faq[:15]]
        parts.append("FAQ:\n" + "\n".join(lines))

    parts.append(
        "Часы работы: Пн-Сб 09:00-18:00. Запись онлайн на сайте или по телефону "
        "+7 (999) 000-00-00."
    )
    return "\n\n".join(parts)


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1, max_length=MAX_QUESTION_CHARS)

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("empty message")
        return value


class AssistantRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=MAX_QUESTION_CHARS)
    history: list[ChatMessage] = Field(default_factory=list, max_length=MAX_HISTORY_MESSAGES)

    @field_validator("question")
    @classmethod
    def strip_question(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("empty question")
        return value


@router.post("/chat")
def assistant_chat(payload: AssistantRequest, request: Request, db=Depends(get_db)):
    api_key = os.getenv("AI_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "AI_ASSISTANT_DISABLED")

    client_key = (request.headers.get("X-Client-ID") or request.client.host if request.client else "")[:255] or "anon"
    if _rate_limited(client_key):
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "RATE_LIMITED")

    context = _build_clinic_context(db)
    messages = [
        {
            "role": "system",
            "content": f"{SYSTEM_PROMPT}\n\nАКТУАЛЬНЫЙ КОНТЕКСТ КЛИНИКИ:\n{context}",
        },
        *[{"role": m.role, "content": m.content} for m in payload.history[-MAX_HISTORY_MESSAGES:]],
        {"role": "user", "content": payload.question},
    ]

    try:
        resp = httpx.post(
            f"{AI_BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": AGENTROUTER_USER_AGENT,
            },
            json={
                "model": AI_MODEL,
                "messages": messages,
                "max_tokens": 400,
                "temperature": 0.3,
            },
            timeout=HTTP_TIMEOUT_SECONDS,
        )
    except httpx.HTTPError:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "AI_UPSTREAM_ERROR") from None

    if resp.status_code in (401, 403):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "AI_AUTH_ERROR")
    if resp.status_code == 429:
        raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "AI_RATE_LIMITED")
    if resp.status_code >= 400:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "AI_UPSTREAM_ERROR")

    try:
        answer = resp.json()["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, ValueError):
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "AI_BAD_RESPONSE") from None
    if not answer:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, "AI_BAD_RESPONSE")

    return {"answer": answer}
