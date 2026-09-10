from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..auth import get_current_admin, get_optional_admin
from ..database import get_db
from ..models import Faq
from ..schemas import FaqBase, FaqOut

router = APIRouter(prefix="/faq", tags=["faq"])


@router.get("", response_model=dict)
def list_faq(include_inactive: bool = Query(False), db: Session = Depends(get_db), admin=Depends(get_optional_admin)):
    if include_inactive and admin is None:
        raise HTTPException(401, "UNAUTHORIZED")
    query = select(Faq).order_by(Faq.sort_order, Faq.id)
    if not include_inactive:
        query = query.where(Faq.is_active.is_(True))
    rows = db.scalars(query).all()
    return {"items": [FaqOut.model_validate(row) for row in rows]}


@router.get("/{faq_id}", response_model=FaqOut)
def get_faq(faq_id: int, db: Session = Depends(get_db), admin=Depends(get_optional_admin)):
    row = db.get(Faq, faq_id)
    if not row or (not row.is_active and admin is None):
        raise HTTPException(404, "NOT_FOUND")
    return row


@router.post("", response_model=FaqOut, status_code=201)
def create_faq(payload: FaqBase, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = Faq(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.put("/{faq_id}", response_model=FaqOut)
def update_faq(faq_id: int, payload: FaqBase, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = db.get(Faq, faq_id)
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    for key, value in payload.model_dump().items():
        setattr(row, key, value)
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    return row


@router.delete("/{faq_id}", status_code=204)
def delete_faq(faq_id: int, db: Session = Depends(get_db), _=Depends(get_current_admin)):
    row = db.get(Faq, faq_id)
    if not row:
        raise HTTPException(404, "NOT_FOUND")
    db.delete(row)
    db.commit()
