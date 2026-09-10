import logging
from datetime import datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Appointment, Doctor, Lead, Service
from ..schemas import AppointmentCreate, AppointmentOut

router = APIRouter(prefix="/appointments", tags=["appointments"])
logger = logging.getLogger(__name__)


def overlaps(db: Session, doctor_id: int, start: datetime, end: datetime, exclude_id: int | None = None) -> bool:
    rows = db.scalars(select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.status.in_(["new", "confirmed"]),
        Appointment.slot_start < end,
    )).all()
    for row in rows:
        service_end = row.slot_start + timedelta(minutes=row.service.duration_minutes)
        if exclude_id != row.id and service_end > start:
            return True
    return False


def validate_booking(db: Session, payload: AppointmentCreate, doctor: Doctor, service: Service):
    start = payload.slot_start
    now = datetime.now()
    day_start = datetime.combine(start.date(), doctor.work_start)
    day_end = datetime.combine(start.date(), doctor.work_end)
    if start <= now or start < day_start or start >= day_end:
        raise HTTPException(422, "INVALID_SLOT")
    elapsed_seconds = (start - day_start).total_seconds()
    if elapsed_seconds % (doctor.slot_minutes * 60):
        raise HTTPException(422, "INVALID_SLOT")
    end = start + timedelta(minutes=service.duration_minutes)
    if end > day_end:
        raise HTTPException(422, "INVALID_SLOT")
    if overlaps(db, doctor.id, start, end):
        raise HTTPException(409, "SLOT_UNAVAILABLE")


@router.post("", response_model=AppointmentOut, status_code=201)
def create_appointment(payload: AppointmentCreate, db: Session = Depends(get_db)):
    doctor = db.get(Doctor, payload.doctor_id)
    service = db.get(Service, payload.service_id)
    if not doctor or not doctor.is_active or not service or not service.is_active:
        raise HTTPException(404, "NOT_FOUND")
    if service not in doctor.services:
        raise HTTPException(422, "DOCTOR_SERVICE_MISMATCH")
    validate_booking(db, payload, doctor, service)
    lead_id = str(uuid4())
    row = Appointment(**payload.model_dump(), lead_id=lead_id)
    row.lead = Lead(lead_id=lead_id, client_id=payload.client_id, source=payload.source,
                    utm_source=payload.utm_source, utm_medium=payload.utm_medium,
                    utm_campaign=payload.utm_campaign, utm_content=payload.utm_content, utm_term=payload.utm_term)
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SLOT_UNAVAILABLE")
    logger.info("Appointment created: doctor_id=%s lead_id=%s phone=%s", doctor.id, lead_id, mask_phone(row.client_phone))
    return row


def mask_phone(phone: str) -> str:
    digits = "".join(ch for ch in phone if ch.isdigit())
    return f"***{digits[-2:]}" if len(digits) >= 2 else "***"
