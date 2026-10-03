from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import require_admin
from ..models import FoundItem, LostReport, Match, MatchStatus, User, Venue
from ..schemas import VenueBasicsOut

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/venue", response_model=VenueBasicsOut)
def venue_basics(
    db: Session = Depends(get_db),
    user: User = Depends(require_admin),
):
    """Admin-only snapshot of the signed-in venue. Staff receive 403."""
    venue = db.query(Venue).filter(Venue.id == user.venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")
    return VenueBasicsOut(
        id=venue.id,
        name=venue.name,
        slug=venue.slug,
        city=venue.city,
        timezone=venue.timezone,
        default_event_name=venue.default_event_name,
        default_event_date=venue.default_event_date,
        lost_report_count=db.query(LostReport)
        .filter(LostReport.venue_id == venue.id)
        .count(),
        found_item_count=db.query(FoundItem)
        .filter(FoundItem.venue_id == venue.id)
        .count(),
        suggested_match_count=db.query(Match)
        .join(LostReport, Match.lost_report_id == LostReport.id)
        .filter(
            LostReport.venue_id == venue.id,
            Match.status == MatchStatus.suggested,
        )
        .count(),
        user_count=db.query(User).filter(User.venue_id == venue.id).count(),
    )
