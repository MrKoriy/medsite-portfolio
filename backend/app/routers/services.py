from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..auth import get_current_admin, get_optional_admin
from ..database import get_db
from ..models import Appointment, Service
from ..schemas import ServiceOut, ServiceBase

router = APIRouter(prefix="/services", tags=["services"])


def service_out(service: Service) -> ServiceOut:
    return ServiceOut.model_validate(service)


@router.get("", response_model=dict)
def list_services(include_inactive: bool = Query(False), db: Session = Depends(get_db), admin=Depends(get_optional_admin)):
    if include_inactive and admin is None:
        raise HTTPException(401, "UNAUTHORIZED")
    query = select(Service).order_by(Service.name, Service.id)
    if not include_inactive:
        query = query.where(Service.is_active.is_(True))
    rows = db.scalars(query).all()
    return {"items": [service_out(row) for row in rows]}


@router.get("/{service_id}", response_model=ServiceOut)
def get_service(service_id: int, db: Session = Depends(get_db), admin=Depends(get_optional_admin)):
    row = db.get(Service, service_id)
    if not row or (not row.is_active and admin is None):
        raise HTTPException(404, "NOT_FOUND")
    return service_out(row)


@router.post("", response_model=ServiceOut, status_code=201)
def create_service(payload: ServiceBase, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = Service(**payload.model_dump())
    db.add(row)
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "CONFLICT")
    return service_out(row)


@router.put("/{service_id}", response_model=ServiceOut)
def update_service(service_id: int, payload: ServiceBase, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = db.get(Service, service_id)
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    row.updated_at = datetime.utcnow()
    try:
        db.commit()
        db.refresh(row)
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "CONFLICT")
    return service_out(row)


@router.delete("/{service_id}", status_code=204)
def delete_service(service_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = db.get(Service, service_id)
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    if db.scalar(select(Appointment.id).where(Appointment.service_id == service_id).limit(1)):
        raise HTTPException(409, "CONFLICT")
    db.delete(row)
    db.commit()
