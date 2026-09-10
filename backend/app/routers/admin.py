from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import ensure_admin, get_current_admin, issue_token, verify_password
from ..database import get_db
from ..models import AdminUser, Appointment, SeoSetting
from ..schemas import AppointmentOut, AppointmentStatus, AppointmentStatusUpdate, LoginRequest, SeoOut, SeoUpdate

router = APIRouter(prefix="/admin", tags=["admin"])
PAGES = {"index", "services", "doctors", "faq", "admin"}


def has_overlap(db: Session, row: Appointment) -> bool:
    end = row.slot_start + timedelta(minutes=row.service.duration_minutes)
    candidates = db.scalars(select(Appointment).where(
        Appointment.id != row.id,
        Appointment.doctor_id == row.doctor_id,
        Appointment.status.in_(["new", "confirmed"]),
        Appointment.slot_start < end,
    )).all()
    return any(candidate.slot_start + timedelta(minutes=candidate.service.duration_minutes) > row.slot_start for candidate in candidates)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.scalar(select(AdminUser).where(AdminUser.username == payload.username))
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "INVALID_CREDENTIALS")
    return {"token": issue_token(user.id), "token_type": "bearer", "expires_in": 28800}


@router.get("/appointments", response_model=dict)
def list_appointments(status: AppointmentStatus | None = Query(None), db: Session = Depends(get_db), _=Depends(get_current_admin)):
    query = select(Appointment).order_by(Appointment.slot_start, Appointment.id)
    if status:
        query = query.where(Appointment.status == status.value)
    return {"items": [AppointmentOut.model_validate(row) for row in db.scalars(query).all()]}


@router.patch("/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, payload: AppointmentStatusUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = db.get(Appointment, appointment_id)
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    if payload.status != AppointmentStatus.cancelled and row.status == "cancelled" and has_overlap(db, row):
        raise HTTPException(409, "SLOT_UNAVAILABLE")
    row.status = payload.status.value
    row.updated_at = datetime.utcnow()
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SLOT_UNAVAILABLE")
    db.refresh(row)
    return row


def setting_or_404(page: str, db: Session) -> SeoSetting:
    if page not in PAGES:
        raise HTTPException(422, "INVALID_PAGE")
    row = db.scalar(select(SeoSetting).where(SeoSetting.page == page))
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    return row


@router.get("/seo/{page}", response_model=SeoOut)
def get_seo(page: str, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    return setting_or_404(page, db)


@router.put("/seo/{page}", response_model=SeoOut)
def put_seo(page: str, payload: SeoUpdate, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    if page not in PAGES:
        raise HTTPException(422, "INVALID_PAGE")
    row = db.scalar(select(SeoSetting).where(SeoSetting.page == page))
    if not row:
        row = SeoSetting(page=page, **payload.model_dump())
        db.add(row)
    else:
        row.title = payload.title
        row.description = payload.description
        row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row
