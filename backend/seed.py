"""Seed Demo Arena + admin/staff users and Night Game sample items."""
from datetime import date

from .auth_utils import hash_password
from .database import SessionLocal, ensure_schema
from .matching import recompute_matches
from .models import FoundItem, LostReport, User, UserRole, Venue

# Documented in README — local demo only
ADMIN_EMAIL = "admin@demoarena.example"
ADMIN_PASSWORD = "DemoArena2026!"
STAFF_EMAIL = "staff@demoarena.example"
STAFF_PASSWORD = "StaffNight2026!"

EVENT_NAME = "Night Game"
EVENT_DATE = date(2026, 10, 1)

LOST_SAMPLES = [
    {
        "reporter_name": "Jordan Fan",
        "reporter_email": "jordan.fan@example.com",
        "reporter_phone": "512-555-0142",
        "item_description": "Black Bluetooth earbuds in a blue charging case",
        "category": "Electronics",
        "color": "Black/Blue",
        "brand": "Generic",
        "section": "112",
        "row": "G",
        "seat": "14",
        "gate": "Gate C",
    },
    {
        "reporter_name": "Sam Guest",
        "reporter_email": "sam.guest@example.com",
        "reporter_phone": "512-555-0177",
        "item_description": "Team scarf",
        "category": "Clothing",
        "color": "Red",
        "section": "204",
        "row": "B",
        "seat": "8",
        "gate": "Gate A",
    },
    {
        "reporter_name": "Alex Rivera",
        "reporter_email": "alex.rivera@example.com",
        "reporter_phone": "512-555-0110",
        "item_description": "Silver car keys with a blue fob",
        "category": "Keys",
        "color": "Silver",
        "section": "118",
        "row": "D",
        "seat": "3",
        "gate": "Gate B",
    },
]

FOUND_SAMPLES = [
    {
        "item_description": "Blue charging case with black earbuds inside",
        "category": "Electronics",
        "color": "Blue",
        "brand": "Generic",
        "section": "112",
        "row": "G",
        "seat": "12",
        "gate": "Gate C",
        "storage_location": "Guest Services — Main Concourse",
        "notes": "Turned in at Guest Services after the game",
    },
    {
        "item_description": "Red team scarf",
        "category": "Clothing",
        "color": "Red",
        "section": "204",
        "row": "B",
        "seat": "9",
        "gate": "Gate A",
        "storage_location": "Guest Services — Main Concourse",
        "notes": "Found on the seat in section 204",
    },
    {
        "item_description": "Blue key fob with silver car keys",
        "category": "Keys",
        "color": "Blue",
        "section": "118",
        "row": "D",
        "seat": "5",
        "gate": "Gate B",
        "storage_location": "Gate B podium",
        "notes": "Handed to gate staff at Gate B",
    },
]


def _fill_blanks(row, spec: dict) -> bool:
    changed = False
    for key, value in spec.items():
        if value is None:
            continue
        if getattr(row, key) in (None, ""):
            setattr(row, key, value)
            changed = True
    return changed


def seed() -> None:
    ensure_schema()
    db = SessionLocal()
    try:
        venue = db.query(Venue).filter(Venue.slug == "demo-arena").first()
        if not venue:
            venue = Venue(
                name="Demo Arena",
                slug="demo-arena",
                city="Austin",
                timezone="America/Chicago",
                default_event_name=EVENT_NAME,
                default_event_date=EVENT_DATE,
            )
            db.add(venue)
            db.flush()
            print(f"Created venue: {venue.name} (id={venue.id})")
        else:
            print(f"Venue already exists: {venue.name} (id={venue.id})")

        admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
        if not admin:
            admin = User(
                venue_id=venue.id,
                email=ADMIN_EMAIL,
                full_name="Demo Arena Admin",
                hashed_password=hash_password(ADMIN_PASSWORD),
                role=UserRole.admin,
            )
            db.add(admin)
            print(f"Created admin: {ADMIN_EMAIL}")
        else:
            print(f"Admin already exists: {ADMIN_EMAIL}")

        staff = db.query(User).filter(User.email == STAFF_EMAIL).first()
        if not staff:
            staff = User(
                venue_id=venue.id,
                email=STAFF_EMAIL,
                full_name="Gate Staff",
                hashed_password=hash_password(STAFF_PASSWORD),
                role=UserRole.staff,
            )
            db.add(staff)
            db.flush()
            print(f"Created staff: {STAFF_EMAIL}")
        else:
            print(f"Staff already exists: {STAFF_EMAIL}")

        for spec in LOST_SAMPLES:
            payload = {
                **spec,
                "event_name": EVENT_NAME,
                "event_date": EVENT_DATE,
            }
            row = (
                db.query(LostReport)
                .filter(
                    LostReport.venue_id == venue.id,
                    LostReport.item_description == spec["item_description"],
                )
                .first()
            )
            if not row:
                db.add(LostReport(venue_id=venue.id, **payload))
                print(f"Seeded lost report: {spec['item_description'][:48]}")
            elif _fill_blanks(row, payload):
                print(f"Filled blank fields on lost report: {spec['item_description'][:48]}")

        for spec in FOUND_SAMPLES:
            payload = {
                **spec,
                "event_name": EVENT_NAME,
                "event_date": EVENT_DATE,
            }
            row = (
                db.query(FoundItem)
                .filter(
                    FoundItem.venue_id == venue.id,
                    FoundItem.item_description == spec["item_description"],
                )
                .first()
            )
            if not row:
                db.add(
                    FoundItem(
                        venue_id=venue.id,
                        logged_by_user_id=staff.id if staff else None,
                        **payload,
                    )
                )
                print(f"Seeded found item: {spec['item_description'][:48]}")
            else:
                if row.logged_by_user_id is None and staff is not None:
                    row.logged_by_user_id = staff.id
                if _fill_blanks(row, payload):
                    print(f"Filled blank fields on found item: {spec['item_description'][:48]}")

        db.commit()
        created = recompute_matches(db)
        print(f"Match recompute created {created} suggested row(s).")
        print("Seed complete.")
        print(f"  Admin login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"  Staff login: {STAFF_EMAIL} / {STAFF_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
