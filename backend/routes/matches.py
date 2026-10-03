from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import require_staff
from ..models import FoundStatus, LostReport, Match, MatchStatus, ReportStatus, User
from ..schemas import MatchDetailOut

router = APIRouter(prefix="/matches", tags=["matches"])


def _query_for_venue(db: Session, user: User):
    return (
        db.query(Match)
        .join(Match.lost_report)
        .filter(LostReport.venue_id == user.venue_id)
        .options(joinedload(Match.lost_report), joinedload(Match.found_item))
    )


def _get_match_or_404(db: Session, user: User, match_id: int) -> Match:
    match = _query_for_venue(db, user).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return match


@router.get("", response_model=List[MatchDetailOut])
def list_matches(
    status: Optional[MatchStatus] = MatchStatus.suggested,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff),
):
    """Staff match queue. Defaults to suggested rows."""
    query = _query_for_venue(db, user)
    if status is not None:
        query = query.filter(Match.status == status)
    rows = query.order_by(Match.created_at.desc()).all()
    seen = set()
    unique_rows = []
    for row in rows:
        if row.id in seen:
            continue
        seen.add(row.id)
        unique_rows.append(row)
    return unique_rows


@router.post("/{match_id}/accept", response_model=MatchDetailOut)
def accept_match(
    match_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff),
):
    match = _get_match_or_404(db, user, match_id)
    if match.status != MatchStatus.suggested:
        raise HTTPException(
            status_code=409,
            detail=f"Only suggested matches can be accepted (current: {match.status.value})",
        )
    match.status = MatchStatus.accepted
    match.lost_report.status = ReportStatus.matched
    match.found_item.status = FoundStatus.matched
    db.commit()
    db.refresh(match)
    return match


@router.post("/{match_id}/reject", response_model=MatchDetailOut)
def reject_match(
    match_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff),
):
    match = _get_match_or_404(db, user, match_id)
    if match.status != MatchStatus.suggested:
        raise HTTPException(
            status_code=409,
            detail=f"Only suggested matches can be rejected (current: {match.status.value})",
        )
    match.status = MatchStatus.rejected
    db.commit()
    db.refresh(match)
    return match
