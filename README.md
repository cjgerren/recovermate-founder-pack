# RecoverMate — Founder Pack (Week 1 Days 3–7)

B2B lost-and-found SaaS. First vertical: **stadium / arena**.  
Pilot venue: fictional **Demo Arena — Night Game** (2026-10-01).

Stack: **FastAPI + SQLAlchemy + SQLite** (backend) · **Vite + React** (frontend).

---

## What this build includes

- Guest **lost-item report** (no login): description, category, section / row / seat / gate, event name and date, contact email and phone, optional photo. Confirmation shows the **report id**.
- **Staff and admin login** (JWT). Guest report and public found-item search stay open.
- **Staff found log** (staff or admin): category, section / gate, event date, notes, optional photo. Recent items are listed.
- **Rule-based match suggestions** (no AI), recomputed inline when a lost report or found item is created:
  - same venue
  - category equal, case-insensitive (both sides must have one)
  - event date on the same calendar day or ±1 day
  - at least one shared keyword on the description or location (section, row, seat, gate, plus color / brand / notes)
- **Match queue**: list `suggested` rows, **Accept** or **Reject**.
  - Accept sets match status `accepted` and marks the lost report and found item `matched` (they stay linked by the match row).
  - Reject sets match status `rejected` and does not link them.
- **Admin venue basics**: name, city, timezone, default event, and simple counts. Staff get 403.
- Seeded Night Game samples that produce suggested matches (earbuds, team scarf, car keys).

## Still out of scope

- SMS / Twilio and real email, including claim notifications
- Stripe billing
- Multi-tenant isolation (single Demo Arena seed)
- AI vision or fuzzy ranking
- Counsel-ready legal documents (`legal/` PDFs are placeholders)
- Production auth hardening

---

## Prerequisites

- Python 3.11+ (tested with 3.13)
- Node.js 18+ and npm

---

## Quick start (local)

### 1. Backend

```bash
cd recovermate-founder-pack

python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r backend/requirements.txt

# Creates SQLite DB + Demo Arena seed (also runs automatically on API startup)
python -m backend.seed

# API on http://127.0.0.1:8000  (docs at /docs)
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

```bash
cd recovermate-founder-pack/frontend
npm install
npm run dev
```

Open **http://127.0.0.1:5173**. Vite proxies `/api`, `/health`, and `/uploads` to the backend.

---

## Demo the match queue

1. Start the API and `npm run dev`.
2. Open **Report Lost Item** and submit a Night Game item (category, section, gate, email/phone, photo). The green confirmation shows **Report ID #…**.
3. Open **Staff Login** and sign in as staff (or admin).
4. Open **Match Queue**. Seeded pairs are already suggested:
   - black earbuds / blue charging case (section 112, Electronics)
   - team scarf (section 204, Clothing)
   - silver car keys / blue fob (section 118, Keys)
5. **Accept** a row. Status becomes `accepted`, and both items show as `matched`. **Reject** leaves them unlinked.
6. To see a new suggestion: as a guest, report something with a category and a distinctive word (for example “purple binoculars”, category Electronics, section 140, date 2026-10-01). Sign in as staff, log a found item with the same category, a date of 2026-10-01 or 2026-10-02, and the word “binoculars”. The queue refreshes with a new suggested row.
7. Admin only: **Venue** shows Demo Arena basics. The staff account cannot open that API.

## Demo Arena seed credentials

| Role  | Email                       | Password          |
|-------|-----------------------------|-------------------|
| Admin | `admin@demoarena.example`   | `DemoArena2026!`  |
| Staff | `staff@demoarena.example`   | `StaffNight2026!` |

- Venue: **Demo Arena** (`slug: demo-arena`, Austin, `America/Chicago`)
- Default event: **Night Game** on **2026-10-01**
- SQLite file: `backend/recovermate.db` (gitignored)

---

## API overview

| Method | Path | Who |
|--------|------|-----|
| GET | `/health` | Public. Liveness + whether Demo Arena is seeded |
| POST | `/api/auth/login` | Public. Email/password → JWT (`role` is `staff` or `admin`) |
| GET | `/api/auth/me` | Any signed-in user |
| GET | `/api/venues` | Public venue name/event for the guest home page |
| GET | `/api/admin/venue` | **Admin.** Venue basics plus counts. Staff → 403 |
| POST | `/api/lost-reports` | **Public.** Create a guest report |
| POST | `/api/lost-reports/{id}/photo` | **Public.** Multipart field `file` |
| GET | `/api/lost-reports` | **Staff or admin** (reports include contact details) |
| GET | `/api/found-items` | Public search (`?q=&section=&venue_id=`) |
| POST | `/api/found-items` | **Staff or admin.** Body includes `notes` |
| POST | `/api/found-items/{id}/photo` | **Staff or admin** |
| GET | `/api/matches?status=suggested` | **Staff or admin.** Also `accepted` or `rejected` |
| POST | `/api/matches/{id}/accept` | **Staff or admin.** Status `accepted`; items become `matched` |
| POST | `/api/matches/{id}/reject` | **Staff or admin.** Status `rejected` |

Scripted check (starts nothing by itself; point it at a running API):

```bash
python scripts/verify_core_loop.py
```

---

## Repo layout

```
recovermate-founder-pack/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── database.py          # SQLite + additive schema upgrade
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── matching.py          # Rule-based suggestions
│   ├── auth_utils.py        # Password hash + JWT
│   ├── seed.py              # Demo Arena seed + sample matches
│   ├── deps.py              # Staff / admin dependencies
│   ├── requirements.txt
│   ├── routes/              # health, auth, venues, admin, lost, found, matches
│   └── uploads/             # Local photo storage
├── frontend/                # Vite + React
│   ├── src/pages/           # Home, Login, ReportItem, Search, StaffFoundLog, MatchQueue, VenueBasics
│   └── package.json
├── scripts/verify_core_loop.py
├── branding/
├── docs/
├── legal/                   # Placeholder PDFs only — not counsel-ready
└── README.md
```

---

## Design choices

- **SQLite** for a zero-config local demo. `RECOVERMATE_DB` overrides the file path.
- **JWT** in `Authorization: Bearer`. Guests never need an account to file a lost report.
- Suggestions are a plain function called at the end of create, not a worker queue. Rejected pairs are not suggested again.
- **Single-venue seed.** Admin “venue basics” is a snapshot of that venue, not a tenant switcher.
- Branding primary `#3A6EA5` / accent `#B0C4DE` from `branding/color_palette.md`.

---

## License / status

Private founder scaffold for Charles Gerren / RecoverMate. Local demo only — not production-ready.
