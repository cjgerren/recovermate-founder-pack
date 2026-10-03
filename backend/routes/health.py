from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Venue
from ..schemas import HealthOut

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.slug == "demo-arena").first()
    return HealthOut(
        status="ok",
        service="RecoverMate API",
        venue_seeded=venue is not None,
    )
