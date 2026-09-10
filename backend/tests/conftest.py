import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.auth import ensure_admin
from app.database import Base, configure_sqlite, get_db
from app import main
from app.main import app


@pytest.fixture()
def client(tmp_path) -> Generator[TestClient, None, None]:
    engine = configure_sqlite(create_engine(f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}))
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with TestingSession() as db:
        old_username = os.environ.get("ADMIN_USERNAME")
        old_password = os.environ.get("ADMIN_PASSWORD")
        os.environ["ADMIN_USERNAME"] = "admin"
        os.environ["ADMIN_PASSWORD"] = "admin"
        ensure_admin(db)
        if old_username is None:
            os.environ.pop("ADMIN_USERNAME")
        else:
            os.environ["ADMIN_USERNAME"] = old_username
        if old_password is None:
            os.environ.pop("ADMIN_PASSWORD")
        else:
            os.environ["ADMIN_PASSWORD"] = old_password

    def override_get_db():
        with TestingSession() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    original_engine = main.engine
    original_session = main.SessionLocal
    main.engine = engine
    main.SessionLocal = TestingSession
    with TestClient(app, raise_server_exceptions=False) as test_client:
        yield test_client
    main.engine = original_engine
    main.SessionLocal = original_session
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)


@pytest.fixture()
def token(client: TestClient) -> str:
    response = client.post("/api/admin/login", json={"username": "admin", "password": "admin"})
    assert response.status_code == 200
    return response.json()["token"]


@pytest.fixture()
def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}
