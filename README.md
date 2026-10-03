# RecoverMate — Founder Pack (Week 1 Day 1)

B2B lost-and-found SaaS. First vertical: **stadium / arena**.  
Pilot venue: fictional **Demo Arena — Night Game**.

Stack: **FastAPI + SQLAlchemy + SQLite** (backend) · **Vite + React** (frontend).

---

## What Day 1 includes

- Runnable monorepo skeleton (backend API + React UI)
- Domain models: `Venue`, `User` (admin/staff), `LostReport`, `FoundItem`, `Match`, `Claim`
- Stadium fields: **section, row, seat, gate/entrance, event_name, event_date** (not flight numbers)
- Seed data: Demo Arena venue, admin + staff users, sample Night Game lost/found rows
- Mounted routes: health, auth (login / me), venues, lost-reports CRUD stub, found-items CRUD stub
- Local photo upload storage under `backend/uploads/` (path stored on models)
- Guest **Report Lost Item** page and staff **Found Log** + **Search** pages with arena/event-night copy

## What Day 1 does **not** include yet

- Real SMS / Twilio notifications
- AI vision or automatic matching
- Stripe billing
- Multi-tenant polish (single Demo Arena seed)
- Production auth hardening
- Counsel-ready legal documents (PDFs under `legal/` remain placeholders — do not treat as real contracts)

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

Open **http://127.0.0.1:5173** — Vite proxies `/api`, `/health`, and `/uploads` to the backend.

---

## Demo Arena seed credentials

| Role  | Email                     | Password         |
|-------|---------------------------|------------------|
| Admin | `admin@demoarena.example`   | `DemoArena2026!` |
| Staff | `staff@demoarena.example`   | `StaffNight2026!` |

- Venue: **Demo Arena** (`slug: demo-arena`)
- Default event: **Night Game** on **2026-10-01**
- SQLite file: `backend/recovermate.db` (gitignored)

---

## API overview

| Method | Path | Notes |
|--------|------|--------|
| GET | `/health` | Liveness + whether venue is seeded |
| POST | `/api/auth/login` | Email/password → JWT |
| GET | `/api/auth/me` | Current user (Bearer token) |
| GET | `/api/venues` | List venues |
| GET/POST | `/api/lost-reports` | Guest lost reports |
| POST | `/api/lost-reports/{id}/photo` | Multipart photo → `uploads/` |
| GET/POST | `/api/found-items` | Staff found-item log + search (`?q=&section=`) |
| POST | `/api/found-items/{id}/photo` | Multipart photo (auth required) |

---

## Repo layout

```
recovermate-founder-pack/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── database.py          # SQLite + session
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth_utils.py        # Password hash + JWT
│   ├── seed.py              # Demo Arena seed
│   ├── deps.py              # Auth dependencies
│   ├── requirements.txt
│   ├── routes/              # health, auth, venues, lost_reports, found_items
│   └── uploads/             # Local photo storage
├── frontend/                # Vite + React
│   ├── src/pages/           # Home, Login, ReportItem, Search, StaffFoundLog
│   └── package.json
├── branding/                # Color palette placeholders
├── docs/                    # High-level notes (stubs)
├── legal/                   # Placeholder PDFs only — not counsel-ready
└── README.md
```

---

## Design choices (Day 1)

- **SQLite** for zero-config local demo; swap URL later for Postgres.
- **JWT** in `Authorization: Bearer` for staff; guests can submit lost reports without login.
- **Single-venue seed** — multi-tenant isolation is intentional future work.
- Branding primary `#3A6EA5` / accent `#B0C4DE` from `branding/color_palette.md`.

---

## License / status

Private founder scaffold for Charles Gerren / RecoverMate. Day 1 local demo only — not production-ready.
