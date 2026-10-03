from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_user, get_optional_user
from ..models import FoundItem, User, Venue
from ..schemas import FoundItemCreate, FoundItemOut

router = APIRouter(prefix="/found-items", tags=["found-items"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=List[FoundItemOut])
def list_found_items(
    venue_id: Optional[int] = None,
    section: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(FoundItem)
    if venue_id is not None:
        query = query.filter(FoundItem.venue_id == venue_id)
    if section:
        query = query.filter(FoundItem.section == section)
    if q:
        like = f"%{q}%"
        query = query.filter(FoundItem.item_description.ilike(like))
    return query.order_by(FoundItem.created_at.desc()).all()


@router.get("/{item_id}", response_model=FoundItemOut)
def get_found_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(FoundItem).filter(FoundItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Found item not found")
    return item


@router.post("", response_model=FoundItemOut, status_code=201)
def create_found_item(
    body: FoundItemCreate,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    venue = db.query(Venue).filter(Venue.id == body.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    event_name = body.event_name or venue.default_event_name
    event_date = body.event_date or venue.default_event_date

    item = FoundItem(
        venue_id=body.venue_id,
        logged_by_user_id=user.id if user else None,
        item_description=body.item_description,
        category=body.category,
        color=body.color,
        brand=body.brand,
        section=body.section,
        row=body.row,
        seat=body.seat,
        gate=body.gate,
        storage_location=body.storage_location,
        event_name=event_name,
        event_date=event_date,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.post("/{item_id}/photo", response_model=FoundItemOut)
async def upload_found_photo(
    item_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    item = db.query(FoundItem).filter(FoundItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Found item not found")

    ext = Path(file.filename or "photo.jpg").suffix or ".jpg"
    filename = f"found_{item_id}_{uuid4().hex[:8]}{ext}"
    dest = UPLOAD_DIR / filename
    content = await file.read()
    dest.write_bytes(content)

    item.photo_path = f"uploads/{filename}"
    db.commit()
    db.refresh(item)
    return item
