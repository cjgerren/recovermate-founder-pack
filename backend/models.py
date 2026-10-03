"""Domain models for stadium/arena lost-and-found."""
from datetime import date, datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class UserRole(str, Enum):
    admin = "admin"
    staff = "staff"


class ReportStatus(str, Enum):
    open = "open"
    matched = "matched"
    claimed = "claimed"
    closed = "closed"


class FoundStatus(str, Enum):
    logged = "logged"
    matched = "matched"
    claimed = "claimed"
    disposed = "disposed"


class MatchStatus(str, Enum):
    suggested = "suggested"
    confirmed = "confirmed"
    rejected = "rejected"


class ClaimStatus(str, Enum):
    pending = "pending"
    verified = "verified"
    released = "released"
    denied = "denied"


class Venue(Base):
    __tablename__ = "venues"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    city: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timezone: Mapped[str] = mapped_column(String(64), default="America/Chicago")
    # Pilot event context (single-venue demo — not multi-tenant yet)
    default_event_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    default_event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    users: Mapped[list["User"]] = relationship(back_populates="venue")
    lost_reports: Mapped[list["LostReport"]] = relationship(back_populates="venue")
    found_items: Mapped[list["FoundItem"]] = relationship(back_populates="venue")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.staff)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    venue: Mapped["Venue"] = relationship(back_populates="users")


class LostReport(Base):
    __tablename__ = "lost_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=False)
    # Guest contact (no account required for Day 1 guest report)
    reporter_name: Mapped[str] = mapped_column(String(200), nullable=False)
    reporter_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reporter_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Item
    item_description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(80), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Stadium location
    section: Mapped[str | None] = mapped_column(String(40), nullable=True)
    row: Mapped[str | None] = mapped_column(String(20), nullable=True)
    seat: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gate: Mapped[str | None] = mapped_column(String(40), nullable=True)
    # Event night context
    event_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[ReportStatus] = mapped_column(
        SAEnum(ReportStatus), default=ReportStatus.open
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    venue: Mapped["Venue"] = relationship(back_populates="lost_reports")
    matches: Mapped[list["Match"]] = relationship(back_populates="lost_report")


class FoundItem(Base):
    __tablename__ = "found_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    venue_id: Mapped[int] = mapped_column(ForeignKey("venues.id"), nullable=False)
    logged_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    item_description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    color: Mapped[str | None] = mapped_column(String(80), nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # Where staff found it
    section: Mapped[str | None] = mapped_column(String(40), nullable=True)
    row: Mapped[str | None] = mapped_column(String(20), nullable=True)
    seat: Mapped[str | None] = mapped_column(String(20), nullable=True)
    gate: Mapped[str | None] = mapped_column(String(40), nullable=True)
    storage_location: Mapped[str | None] = mapped_column(String(200), nullable=True)
    event_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    photo_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    status: Mapped[FoundStatus] = mapped_column(
        SAEnum(FoundStatus), default=FoundStatus.logged
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    venue: Mapped["Venue"] = relationship(back_populates="found_items")
    matches: Mapped[list["Match"]] = relationship(back_populates="found_item")


class Match(Base):
    """Manual/stub match link — AI matching is out of scope for Day 1."""

    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    lost_report_id: Mapped[int] = mapped_column(
        ForeignKey("lost_reports.id"), nullable=False
    )
    found_item_id: Mapped[int] = mapped_column(
        ForeignKey("found_items.id"), nullable=False
    )
    status: Mapped[MatchStatus] = mapped_column(
        SAEnum(MatchStatus), default=MatchStatus.suggested
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    lost_report: Mapped["LostReport"] = relationship(back_populates="matches")
    found_item: Mapped["FoundItem"] = relationship(back_populates="matches")
    claim: Mapped["Claim | None"] = relationship(back_populates="match", uselist=False)


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(
        ForeignKey("matches.id"), unique=True, nullable=False
    )
    claimant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    claimant_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    claimant_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ClaimStatus] = mapped_column(
        SAEnum(ClaimStatus), default=ClaimStatus.pending
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    match: Mapped["Match"] = relationship(back_populates="claim")
