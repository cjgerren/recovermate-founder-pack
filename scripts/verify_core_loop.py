#!/usr/bin/env python3
"""Scripted check for the RecoverMate core loop (Days 3–7).

Talks to a running API (default http://127.0.0.1:8000). Exits non-zero on failure.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.environ.get("RECOVERMATE_BASE", "http://127.0.0.1:8000").rstrip("/")
STAFF_EMAIL = "staff@demoarena.example"
STAFF_PASSWORD = "StaffNight2026!"
ADMIN_EMAIL = "admin@demoarena.example"
ADMIN_PASSWORD = "DemoArena2026!"


def req(method: str, path: str, body=None, token: str | None = None, form=None, expect: int | None = None):
    headers = {}
    data = None
    if form is not None:
        data, content_type = form
        headers["Content-Type"] = content_type
    elif body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            status = response.status
            raw = response.read()
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read()
    parsed = None
    if raw:
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = raw.decode()
    if expect is not None and status != expect:
        raise SystemExit(f"FAIL {method} {path} expected {expect} got {status}: {parsed}")
    return status, parsed


def multipart(filename: str, content: bytes, content_type: str = "image/jpeg"):
    boundary = "----RecoverMateVerify"
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: {content_type}\r\n\r\n"
    ).encode() + content + f"\r\n--{boundary}--\r\n".encode()
    return body, f"multipart/form-data; boundary={boundary}"


def find_pair(rows, lost_id: int, found_id: int):
    for row in rows:
        if row["lost_report_id"] == lost_id and row["found_item_id"] == found_id:
            return row
    return None


def main() -> None:
    status, health = req("GET", "/health", expect=200)
    if health.get("venue_seeded") is not True:
        raise SystemExit(f"FAIL seed did not mark venue_seeded: {health}")
    print("PASS health venue seeded")

    req("POST", "/api/found-items", body={"item_description": "nope", "venue_id": 1}, expect=401)
    req("GET", "/api/matches", expect=401)
    req("GET", "/api/lost-reports", expect=401)
    req("GET", "/api/admin/venue", expect=401)
    print("PASS staff/admin routes reject anonymous calls")

    _, staff_login = req(
        "POST",
        "/api/auth/login",
        body={"email": STAFF_EMAIL, "password": STAFF_PASSWORD},
        expect=200,
    )
    if staff_login.get("role") != "staff":
        raise SystemExit(f"FAIL staff role: {staff_login}")
    staff = staff_login["access_token"]
    print("PASS staff login")

    _, suggested = req("GET", "/api/matches?status=suggested", token=staff, expect=200)
    earbuds = [
        row
        for row in suggested
        if "earbuds" in row["lost_report"]["item_description"].lower()
        and "earbuds" in row["found_item"]["item_description"].lower()
    ]
    if not earbuds:
        raise SystemExit(f"FAIL seed did not suggest the earbuds pair: {suggested}")
    print(f"PASS seed suggested earbuds match #{earbuds[0]['id']}")

    lost_body = {
        "venue_id": 1,
        "reporter_name": "Casey Guest",
        "reporter_email": "casey.guest@example.com",
        "reporter_phone": "512-555-0199",
        "item_description": "Blue water bottle with stadium logo",
        "category": "Other",
        "section": "140",
        "row": "F",
        "seat": "9",
        "gate": "Gate D",
        "event_name": "Night Game",
        "event_date": "2026-10-01",
    }
    _, lost = req("POST", "/api/lost-reports", body=lost_body, expect=201)
    for field in (
        "id",
        "reporter_email",
        "reporter_phone",
        "section",
        "row",
        "seat",
        "gate",
        "event_name",
        "event_date",
        "category",
    ):
        if not lost.get(field):
            raise SystemExit(f"FAIL lost report missing {field}: {lost}")
    if lost["reporter_email"] != lost_body["reporter_email"]:
        raise SystemExit("FAIL email not persisted")
    if lost["section"] != "140" or lost["gate"] != "Gate D":
        raise SystemExit("FAIL location not persisted")
    print(f"PASS public lost report #{lost['id']}")

    _, with_photo = req(
        "POST",
        f"/api/lost-reports/{lost['id']}/photo",
        form=multipart("bottle.jpg", b"\xff\xd8\xff\xd9"),
        expect=200,
    )
    if not with_photo.get("photo_path"):
        raise SystemExit(f"FAIL photo_path missing: {with_photo}")
    print(f"PASS lost photo stored at {with_photo['photo_path']}")

    _, reread = req("GET", f"/api/lost-reports/{lost['id']}", token=staff, expect=200)
    if reread["photo_path"] != with_photo["photo_path"] or reread["seat"] != "9":
        raise SystemExit(f"FAIL reread mismatch: {reread}")
    print("PASS staff can read the saved guest report")

    found_body = {
        "venue_id": 1,
        "item_description": "Blue water bottle with stadium logo",
        "category": "other",
        "section": "140",
        "gate": "Gate D",
        "event_name": "Night Game",
        "event_date": "2026-10-02",
        "notes": "Turned in one day later at Gate D",
    }
    _, found = req("POST", "/api/found-items", body=found_body, token=staff, expect=201)
    if found.get("notes") != found_body["notes"] or found.get("logged_by_user_id") is None:
        raise SystemExit(f"FAIL found item not attributed or notes dropped: {found}")
    _, found_photo = req(
        "POST",
        f"/api/found-items/{found['id']}/photo",
        token=staff,
        form=multipart("found-bottle.jpg", b"\xff\xd8\xff\xd9"),
        expect=200,
    )
    if not found_photo.get("photo_path"):
        raise SystemExit("FAIL found photo missing")
    print(f"PASS staff found item #{found['id']} (category case + date +1 day)")

    _, suggested = req("GET", "/api/matches?status=suggested", token=staff, expect=200)
    water = find_pair(suggested, lost["id"], found["id"])
    if not water or water["status"] != "suggested":
        raise SystemExit(f"FAIL water bottle pair not suggested: {suggested}")
    print(f"PASS suggested match #{water['id']} ({water.get('notes')})")

    _, decoy_lost = req(
        "POST",
        "/api/lost-reports",
        body={
            "venue_id": 1,
            "reporter_name": "Pat Guest",
            "reporter_email": "pat.guest@example.com",
            "item_description": "Only a laptop sleeve",
            "category": "Electronics",
            "section": "500",
            "gate": "North Tunnel",
            "event_name": "Night Game",
            "event_date": "2026-10-01",
        },
        expect=201,
    )
    _, decoy_found = req(
        "POST",
        "/api/found-items",
        body={
            "venue_id": 1,
            "item_description": "Wool scarf from the concourse",
            "category": "Electronics",
            "section": "330",
            "gate": "South Plaza",
            "event_name": "Night Game",
            "event_date": "2026-10-01",
            "notes": "Different object, same category and night",
        },
        token=staff,
        expect=201,
    )
    _, far_found = req(
        "POST",
        "/api/found-items",
        body={
            "venue_id": 1,
            "item_description": "Only a laptop sleeve",
            "category": "Electronics",
            "section": "500",
            "gate": "North Tunnel",
            "event_name": "Night Game",
            "event_date": "2026-10-05",
        },
        token=staff,
        expect=201,
    )
    _, suggested = req("GET", "/api/matches?status=suggested", token=staff, expect=200)
    if find_pair(suggested, decoy_lost["id"], decoy_found["id"]):
        raise SystemExit("FAIL keyword rule suggested an unrelated pair")
    if find_pair(suggested, decoy_lost["id"], far_found["id"]):
        raise SystemExit("FAIL date window suggested a pair four days apart")
    print("PASS category/date/keyword rules skipped non-matches")

    _, accepted = req("POST", f"/api/matches/{water['id']}/accept", token=staff, expect=200)
    if accepted["status"] != "accepted":
        raise SystemExit(f"FAIL accept status: {accepted}")
    if accepted["lost_report"]["status"] != "matched" or accepted["found_item"]["status"] != "matched":
        raise SystemExit(f"FAIL accept did not link items: {accepted}")
    _, lost_after = req("GET", f"/api/lost-reports/{lost['id']}", token=staff, expect=200)
    _, found_after = req("GET", f"/api/found-items/{found['id']}", expect=200)
    if lost_after["status"] != "matched" or found_after["status"] != "matched":
        raise SystemExit("FAIL linked statuses did not persist")
    print(f"PASS staff accepted match #{water['id']} and linked lost+found")

    _, rejected = req(
        "POST",
        f"/api/matches/{earbuds[0]['id']}/reject",
        token=staff,
        expect=200,
    )
    if rejected["status"] != "rejected":
        raise SystemExit(f"FAIL reject status: {rejected}")
    print(f"PASS staff rejected match #{earbuds[0]['id']}")

    req("GET", "/api/admin/venue", token=staff, expect=403)
    print("PASS staff cannot read admin venue basics")

    _, admin_login = req(
        "POST",
        "/api/auth/login",
        body={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        expect=200,
    )
    if admin_login.get("role") != "admin":
        raise SystemExit(f"FAIL admin role: {admin_login}")
    admin = admin_login["access_token"]
    _, basics = req("GET", "/api/admin/venue", token=admin, expect=200)
    if basics.get("name") != "Demo Arena" or basics.get("default_event_name") != "Night Game":
        raise SystemExit(f"FAIL venue basics: {basics}")
    if basics.get("suggested_match_count", 0) < 1:
        raise SystemExit(f"FAIL expected remaining suggestions: {basics}")
    _, admin_matches = req("GET", "/api/matches?status=accepted", token=admin, expect=200)
    if not find_pair(admin_matches, lost["id"], found["id"]):
        raise SystemExit("FAIL admin could not see the accepted match")
    print("PASS admin login, venue basics, and staff-level match read")
    print("ALL CHECKS PASSED")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.URLError as exc:
        raise SystemExit(f"FAIL could not reach {BASE}: {exc}") from exc
