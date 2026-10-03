from pathlib import Path
from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import LostReport, Venue
from ..schemas import LostReportCreate, LostReportOut

router = APIRouter(prefix="/lost-reports", tags=["lost-reports"])

UPLOAD_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("", response_model=List[LostReportOut])
def list_lost_reports(
    venue_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    q = db.query(LostReport)
    if venue_id is not None:
        q = q.filter(LostReport.venue_id == venue_id)
    return q.order_by(LostReport.created_at.desc()).all()


@router.get("/{report_id}", response_model=LostReportOut)
def get_lost_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(LostReport).filter(LostReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lost report not found")
    return report


@router.post("", response_model=LostReportOut, status_code=201)
def create_lost_report(body: LostReportCreate, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.id == body.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    # Default event context from venue if guest left blank
    event_name = body.event_name or venue.default_event_name
    event_date = body.event_date or venue.default_event_date

    report = LostReport(
        venue_id=body.venue_id,
        reporter_name=body.reporter_name,
        reporter_email=str(body.reporter_email) if body.reporter_email else None,
        reporter_phone=body.reporter_phone,
        item_description=body.item_description,
        category=body.category,
        color=body.color,
        brand=body.brand,
        section=body.section,
        row=body.row,
        seat=body.seat,
        gate=body.gate,
        event_name=event_name,
        event_date=event_date,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.post("/{report_id}/photo", response_model=LostReportOut)
async def upload_lost_photo(
    report_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    report = db.query(LostReport).filter(LostReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Lost report not found")

    ext = Path(file.filename or "photo.jpg").suffix or ".jpg"
    filename = f"lost_{report_id}_{uuid4().hex[:8]}{ext}"
    dest = UPLOAD_DIR / filename
    content = await file.read()
    dest.write_bytes(content)

    report.photo_path = f"uploads/{filename}"
    db.commit()
    db.refresh(report)
    return report
