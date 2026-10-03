"""Pydantic schemas for API request/response."""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .models import (
    ClaimStatus,
    FoundStatus,
    MatchStatus,
    ReportStatus,
    UserRole,
)


# --- Auth ---
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    full_name: str
    venue_id: int


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    venue_id: int
    is_active: bool

    model_config = {"from_attributes": True}


# --- Venue ---
class VenueOut(BaseModel):
    id: int
    name: str
    slug: str
    city: Optional[str] = None
    timezone: str
    default_event_name: Optional[str] = None
    default_event_date: Optional[date] = None

    model_config = {"from_attributes": True}


# --- Lost reports ---
class LostReportCreate(BaseModel):
    venue_id: int = 1
    reporter_name: str = Field(..., min_length=1, max_length=200)
    reporter_email: Optional[EmailStr] = None
    reporter_phone: Optional[str] = None
    item_description: str = Field(..., min_length=1)
    category: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    section: Optional[str] = None
    row: Optional[str] = None
    seat: Optional[str] = None
    gate: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[date] = None


class LostReportOut(BaseModel):
    id: int
    venue_id: int
    reporter_name: str
    reporter_email: Optional[str] = None
    reporter_phone: Optional[str] = None
    item_description: str
    category: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    section: Optional[str] = None
    row: Optional[str] = None
    seat: Optional[str] = None
    gate: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[date] = None
    photo_path: Optional[str] = None
    status: ReportStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Found items ---
class FoundItemCreate(BaseModel):
    venue_id: int = 1
    item_description: str = Field(..., min_length=1)
    category: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    section: Optional[str] = None
    row: Optional[str] = None
    seat: Optional[str] = None
    gate: Optional[str] = None
    storage_location: Optional[str] = None
    notes: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[date] = None


class FoundItemOut(BaseModel):
    id: int
    venue_id: int
    logged_by_user_id: Optional[int] = None
    item_description: str
    category: Optional[str] = None
    color: Optional[str] = None
    brand: Optional[str] = None
    section: Optional[str] = None
    row: Optional[str] = None
    seat: Optional[str] = None
    gate: Optional[str] = None
    storage_location: Optional[str] = None
    notes: Optional[str] = None
    event_name: Optional[str] = None
    event_date: Optional[date] = None
    photo_path: Optional[str] = None
    status: FoundStatus
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Matches ---
class MatchOut(BaseModel):
    id: int
    lost_report_id: int
    found_item_id: int
    status: MatchStatus
    notes: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class MatchDetailOut(MatchOut):
    lost_report: LostReportOut
    found_item: FoundItemOut


class VenueBasicsOut(VenueOut):
    lost_report_count: int
    found_item_count: int
    suggested_match_count: int
    user_count: int


class ClaimOut(BaseModel):
    id: int
    match_id: int
    claimant_name: str
    claimant_email: Optional[str] = None
    claimant_phone: Optional[str] = None
    status: ClaimStatus
    created_at: datetime

    model_config = {"from_attributes": True}


class HealthOut(BaseModel):
    status: str
    service: str
    venue_seeded: bool
