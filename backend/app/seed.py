"""Seed the public catalogue into a freshly created database.

A serverless deployment recreates the SQLite file on every cold start, so the
marketing content lives in seed.json under version control instead of only in
the developer's local database. An existing installation is left untouched;
`MEDSITE_SEED=0` disables seeding entirely (tests do this to keep a clean DB).
"""
from __future__ import annotations

import json
import os
from datetime import time
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Doctor, Faq, Service

SEED_PATH = Path(__file__).resolve().parents[1] / "seed.json"


def seed_catalogue(db: Session) -> None:
    if os.getenv("MEDSITE_SEED", "1") == "0":
        return
    if not SEED_PATH.exists() or db.scalar(select(Service.id).limit(1)):
        return

    data = json.loads(SEED_PATH.read_text(encoding="utf-8"))

    services: dict[str, Service] = {}
    for row in data.get("services", []):
        services[row["name"]] = service = Service(**row)
        db.add(service)

    doctors: dict[str, Doctor] = {}
    for row in data.get("doctors", []):
        row = dict(row)
        row["work_start"] = time.fromisoformat(row["work_start"])
        row["work_end"] = time.fromisoformat(row["work_end"])
        doctors[row["full_name"]] = doctor = Doctor(**row)
        db.add(doctor)

    for row in data.get("faq", []):
        db.add(Faq(**row))

    db.flush()

    for link in data.get("doctor_services", []):
        doctor = doctors.get(link["doctor"])
        service = services.get(link["service"])
        if doctor is not None and service is not None and service not in doctor.services:
            doctor.services.append(service)

    db.commit()
