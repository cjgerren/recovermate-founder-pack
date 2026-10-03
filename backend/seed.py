"""Seed Demo Arena + admin/staff users for local Night Game pilot."""
from datetime import date

from .auth_utils import hash_password
from .database import Base, SessionLocal, engine
from .models import FoundItem, LostReport, User, UserRole, Venue

# Documented in README — local demo only
ADMIN_EMAIL = "admin@demoarena.example"
ADMIN_PASSWORD = "DemoArena2026!"
STAFF_EMAIL = "staff@demoarena.example"
STAFF_PASSWORD = "StaffNight2026!"

EVENT_NAME = "Night Game"
EVENT_DATE = date(2026, 10, 1)


def seed() -> None:
    Base.metadata.create_all(bind=engine)
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
            print(f"Created staff: {STAFF_EMAIL}")
        else:
            print(f"Staff already exists: {STAFF_EMAIL}")

        # Sample lost report (guest)
        if db.query(LostReport).count() == 0:
            db.add(
                LostReport(
                    venue_id=venue.id,
                    reporter_name="Jordan Fan",
                    reporter_email="jordan.fan@example.com",
                    reporter_phone="512-555-0142",
                    item_description="Black Bluetooth earbuds in a blue charging case",
                    category="Electronics",
                    color="Black/Blue",
                    brand="Generic",
                    section="112",
                    row="G",
                    seat="14",
                    gate="Gate C",
                    event_name=EVENT_NAME,
                    event_date=EVENT_DATE,
                )
            )
            print("Seeded sample lost report (section 112 / row G / seat 14)")

        # Sample found item (staff log)
        if db.query(FoundItem).count() == 0:
            db.add(
                FoundItem(
                    venue_id=venue.id,
                    logged_by_user_id=None,
                    item_description="Blue charging case with black earbuds inside",
                    category="Electronics",
                    color="Blue",
                    brand="Generic",
                    section="112",
                    row="G",
                    seat="12",
                    gate="Gate C",
                    storage_location="Guest Services — Main Concourse",
                    event_name=EVENT_NAME,
                    event_date=EVENT_DATE,
                )
            )
            print("Seeded sample found item (section 112)")

        db.commit()
        print("Seed complete.")
        print(f"  Admin login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
        print(f"  Staff login: {STAFF_EMAIL} / {STAFF_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
