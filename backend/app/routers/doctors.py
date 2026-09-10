from datetime import date, datetime, time, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import get_current_admin, get_optional_admin
from ..database import get_db
from ..models import Appointment, Doctor, Service
from ..schemas import DoctorBase, DoctorOut

router = APIRouter(prefix="/doctors", tags=["doctors"])


def doctor_out(row: Doctor) -> DoctorOut:
    values = {key: getattr(row, key) for key in DoctorOut.model_fields if key != "service_ids"}
    values["service_ids"] = [service.id for service in row.services]
    return DoctorOut.model_validate(values)


def validate_services(db: Session, service_ids: list[int]) -> list[Service]:
    rows = db.scalars(select(Service).where(Service.id.in_(service_ids))).all()
    if len(rows) != len(service_ids):
        raise HTTPException(404, "NOT_FOUND")
    return rows


@router.get("", response_model=dict)
def list_doctors(service_id: int | None = Query(None), include_inactive: bool = Query(False), db: Session = Depends(get_db), admin=Depends(get_optional_admin)):
    if include_inactive and admin is None:
        raise HTTPException(401, "UNAUTHORIZED")
    query = select(Doctor).order_by(Doctor.full_name, Doctor.id)
    if not include_inactive:
        query = query.where(Doctor.is_active.is_(True))
    if service_id is not None:
        query = query.join(Doctor.services).where(Service.id == service_id)
    return {"items": [doctor_out(row) for row in db.scalars(query).unique().all()]}


@router.get("/{doctor_id}", response_model=DoctorOut)
def get_doctor(doctor_id: int, db: Session = Depends(get_db), admin=Depends(get_optional_admin)):
    row = db.get(Doctor, doctor_id)
    if not row or (not row.is_active and admin is None):
        raise HTTPException(404, "NOT_FOUND")
    return doctor_out(row)


@router.post("", response_model=DoctorOut, status_code=201)
def create_doctor(payload: DoctorBase, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = Doctor(**payload.model_dump(exclude={"service_ids"}))
    row.services = validate_services(db, payload.service_ids)
    db.add(row)
    db.commit()
    db.refresh(row)
    return doctor_out(row)


@router.put("/{doctor_id}", response_model=DoctorOut)
def update_doctor(doctor_id: int, payload: DoctorBase, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = db.get(Doctor, doctor_id)
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    for key, value in payload.model_dump(exclude={"service_ids"}).items():
        setattr(row, key, value)
    row.services = validate_services(db, payload.service_ids)
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return doctor_out(row)


@router.delete("/{doctor_id}", status_code=204)
def delete_doctor(doctor_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = db.get(Doctor, doctor_id)
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    if db.scalar(select(Appointment.id).where(Appointment.doctor_id == doctor_id).limit(1)):
        raise HTTPException(409, "CONFLICT")
    db.delete(row)
    db.commit()


@router.get("/{doctor_id}/slots")
def slots(doctor_id: int, date: date = Query(...), db: Session = Depends(get_db)):
    doctor = db.get(Doctor, doctor_id)
    if not doctor or not doctor.is_active:
        raise HTTPException(404, "NOT_FOUND")
    start = datetime.combine(date, doctor.work_start)
    end = datetime.combine(date, doctor.work_end)
    occupied = db.scalars(select(Appointment).where(
        Appointment.doctor_id == doctor_id,
        Appointment.slot_start >= start,
        Appointment.slot_start < end,
        Appointment.status.in_(["new", "confirmed"]),
    )).all()
    now = datetime.now()
    result = []
    cursor = start
    while cursor < end:
        is_occupied = any(
            appointment.slot_start < cursor + timedelta(minutes=doctor.slot_minutes)
            and appointment.slot_start + timedelta(minutes=appointment.service.duration_minutes) > cursor
            for appointment in occupied
        )
        if cursor > now and not is_occupied:
            result.append(cursor.isoformat(timespec="seconds"))
        cursor += timedelta(minutes=doctor.slot_minutes)
    return {"doctor_id": doctor_id, "date": date.isoformat(), "slots": result}
