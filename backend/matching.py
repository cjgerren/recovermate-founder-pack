"""Rule-based lost/found suggestions. No AI and no background job queue."""
from __future__ import annotations

import re
from datetime import date

from sqlalchemy.orm import Session

from .models import FoundItem, LostReport, Match, MatchStatus

# Shared filler words are not enough to suggest a match.
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "its",
    "left",
    "my",
    "of",
    "on",
    "or",
    "our",
    "the",
    "to",
    "was",
    "were",
    "with",
}

# Same calendar day or one day on either side.
DATE_WINDOW_DAYS = 1


def _tokens(value: str | None) -> set[str]:
    if not value:
        return set()
    found: set[str] = set()
    for word in re.findall(r"[a-z0-9]+", value.lower()):
        if word in STOPWORDS:
            continue
        has_digit = any(ch.isdigit() for ch in word)
        if has_digit and len(word) >= 2:
            found.add(word)
        elif not has_digit and len(word) >= 3:
            found.add(word)
    return found


def _gate_tokens(value: str | None) -> set[str]:
    """Keep Gate C distinct from Gate A.

    The literal word "gate" is on almost every row, so it must not count as
    overlap by itself. "Gate C" becomes the single token "gatec".
    """
    if not value:
        return set()
    raw = value.strip().lower()
    labeled = re.fullmatch(r"gate\s*([a-z0-9]+)", raw)
    if labeled:
        return {f"gate{labeled.group(1)}"}
    return _tokens(raw) - {"gate"}


def _blob(item: LostReport | FoundItem) -> set[str]:
    parts = [
        item.item_description,
        item.category,
        item.color,
        item.brand,
        item.section,
        item.row,
        item.seat,
        getattr(item, "storage_location", None),
        getattr(item, "notes", None),
    ]
    tokens: set[str] = set()
    for part in parts:
        tokens |= _tokens(part)
    tokens |= _gate_tokens(item.gate)
    return tokens


def _categories_overlap(left: str | None, right: str | None) -> bool:
    if not left or not right:
        return False
    return left.strip().lower() == right.strip().lower()


def _dates_overlap(left: date | None, right: date | None) -> bool:
    if left is None or right is None:
        return False
    return abs((left - right).days) <= DATE_WINDOW_DAYS


def match_keywords(lost: LostReport, found: FoundItem) -> set[str]:
    """Return overlapping keywords when the pair meets every rule, else empty.

    Rules (all required):
    - same venue
    - category equal, case-insensitive (both must be set)
    - event dates within ±1 calendar day
    - at least one shared keyword from description, location, or section
    """
    if lost.venue_id != found.venue_id:
        return set()
    if not _categories_overlap(lost.category, found.category):
        return set()
    if not _dates_overlap(lost.event_date, found.event_date):
        return set()
    # Category is already required on its own; keyword overlap uses the
    # description / location / section fields (plus color, brand, notes).
    lost_tokens = _blob(lost) - _tokens(lost.category)
    found_tokens = _blob(found) - _tokens(found.category)
    return lost_tokens & found_tokens


def recompute_matches(db: Session) -> int:
    """Insert missing suggested Match rows for every pair that passes the rules.

    Existing pairs are left alone, including accepted and rejected rows, so a
    staff decision is not overwritten. Safe to call inline after a create.
    """
    losts = db.query(LostReport).all()
    founds = db.query(FoundItem).all()
    existing = {
        (lost_id, found_id)
        for lost_id, found_id in db.query(Match.lost_report_id, Match.found_item_id).all()
    }
    created = 0
    for lost in losts:
        for found in founds:
            key = (lost.id, found.id)
            if key in existing:
                continue
            keywords = match_keywords(lost, found)
            if not keywords:
                continue
            db.add(
                Match(
                    lost_report_id=lost.id,
                    found_item_id=found.id,
                    status=MatchStatus.suggested,
                    notes="keywords: " + ", ".join(sorted(keywords)),
                )
            )
            existing.add(key)
            created += 1
    # Keep suggested notes aligned with the current rules. Accepted and
    # rejected rows are not rewritten.
    dirty = False
    suggested = (
        db.query(Match)
        .filter(Match.status == MatchStatus.suggested)
        .all()
    )
    lost_by_id = {row.id: row for row in losts}
    found_by_id = {row.id: row for row in founds}
    for match in suggested:
        keywords = match_keywords(
            lost_by_id.get(match.lost_report_id),
            found_by_id.get(match.found_item_id),
        ) if match.lost_report_id in lost_by_id and match.found_item_id in found_by_id else set()
        if not keywords:
            continue
        notes = "keywords: " + ", ".join(sorted(keywords))
        if match.notes != notes:
            match.notes = notes
            dirty = True
    if created or dirty:
        db.commit()
    return created
