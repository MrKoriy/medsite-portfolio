import logging
import os
import re
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .auth import ensure_admin
from .database import Base, SessionLocal, engine
from .routers import admin, appointments, assistant, doctors, faq, health, services


class PhoneMaskFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        message = record.getMessage()
        record.msg = re.sub(r"(?<!\w)\+?\d[\d ()-]{7,}\d", "***", message)
        record.args = ()
        return True


logging.getLogger("app").addFilter(PhoneMaskFilter())


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        ensure_admin(db)
    yield


app = FastAPI(title="Medsite API", lifespan=lifespan)
origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:8000,http://127.0.0.1:8000").split(",") if origin.strip()]
if "*" in origins:
    raise RuntimeError("CORS_ORIGINS must contain explicit origins")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type", "X-Client-ID"],
)
app.include_router(health.router, prefix="/api")
app.include_router(services.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(faq.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")


def error_response(code: str, message: str):
    return JSONResponse(status_code=400, content={"error": {"code": code, "message": message}})


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc):
    status_codes = {400: "BAD_REQUEST", 401: "UNAUTHORIZED", 404: "NOT_FOUND", 409: "CONFLICT", 422: "VALIDATION_ERROR"}
    detail = exc.detail if isinstance(exc.detail, str) else None
    code = detail if detail and detail.replace("_", "").isupper() else status_codes.get(exc.status_code, "HTTP_ERROR")
    messages = {
        "UNAUTHORIZED": "Authentication is required",
        "INVALID_CREDENTIALS": "Invalid username or password",
        "NOT_FOUND": "Resource not found",
        "SLOT_UNAVAILABLE": "The selected slot is unavailable",
        "CONFLICT": "The request conflicts with existing data",
        "VALIDATION_ERROR": "Invalid request",
        "AI_ASSISTANT_DISABLED": "AI assistant is not configured",
        "AI_UPSTREAM_ERROR": "AI assistant is temporarily unavailable",
        "AI_AUTH_ERROR": "AI assistant is temporarily unavailable",
        "AI_RATE_LIMITED": "Too many requests, please slow down",
        "AI_BAD_RESPONSE": "AI assistant is temporarily unavailable",
        "RATE_LIMITED": "Too many requests, please slow down",
    }
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": code, "message": messages.get(code, detail or "Request failed")}})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": {"code": "VALIDATION_ERROR", "message": "Invalid request"}})


@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    return JSONResponse(status_code=409, content={"error": {"code": "CONFLICT", "message": "Conflict"}})


@app.exception_handler(ResponseValidationError)
async def response_validation_exception_handler(request: Request, exc: ResponseValidationError):
    logging.getLogger(__name__).exception("Response validation failed", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled application error", exc_info=exc)
    return JSONResponse(status_code=500, content={"error": {"code": "INTERNAL_ERROR", "message": "Internal server error"}})


from fastapi.staticfiles import StaticFiles
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")

