from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.main import app
from app.models.profiles import MentorProfile
from app.models.user import User, UserRole


def _register_and_login(client, payload):
    client.post("/auth/register", json=payload)
    identifier = payload.get("email") or payload.get("mobile_number")
    client.post("/auth/login", json={"identifier": identifier, "password": payload["password"]})


def test_non_admin_blocked(student_client):
    res = student_client.get("/admin/guardian-relationships")
    assert res.status_code == 403


def test_grant_fails_for_nonexistent_relationship(admin_client):
    fake_id = "00000000-0000-0000-0000-000000000000"
    res = admin_client.post(f"/admin/guardian-relationships/{fake_id}/consent/mentorship/grant")
    assert res.status_code == 404


def test_full_admin_override_chain(admin_client, db_session):
    student = TestClient(app)
    parent = TestClient(app)

    _register_and_login(
        student,
        {
            "full_name": "Override Chain Student",
            "role": "student",
            "mobile_number": "9940000001",
            "password": "TestPass123!",
            "date_of_birth": "2010-01-01",
            "school_name": "School",
            "parent_name": "Parent",
            "parent_relation": "Mother",
            "address": "addr",
            "district": "d",
            "state": "Delhi",
        },
    )
    _register_and_login(
        parent,
        {
            "full_name": "Override Chain Parent",
            "role": "parent",
            "email": "override-chain-parent@example.com",
            "mobile_number": "9940000002",
            "password": "TestPass123!",
            "student_name": "Override Chain Student",
            "relation_to_student": "Mother",
        },
    )

    invite = student.post(
        "/students/me/guardians", json={"parent_email": "override-chain-parent@example.com"}
    )
    relationship_id = invite.json()["id"]

    still_blocked = admin_client.post(
        f"/admin/guardian-relationships/{relationship_id}/consent/mentorship/grant"
    )
    assert still_blocked.status_code == 400

    parent.post(f"/parents/me/guardians/{relationship_id}/verify")

    listing = admin_client.get("/admin/guardian-relationships").json()
    mine = next(r for r in listing if r["id"] == relationship_id)
    assert mine["status"] == "verified"
    assert mine["consents"] == []

    grant = admin_client.post(
        f"/admin/guardian-relationships/{relationship_id}/consent/mentorship/grant"
    )
    assert grant.status_code == 200
    assert grant.json()["consents"] == [{"consent_type": "mentorship", "status": "granted"}]

    # Proves the grant is real, not cosmetic: the mentorship request
    # gate (student_has_any_active_consent) actually reads it.
    mentor_user = User(
        email="override-chain-mentor@example.com",
        full_name="Override Chain Mentor",
        role=UserRole.MENTOR,
        hashed_password=hash_password("TestPass123!"),
    )
    db_session.add(mentor_user)
    db_session.commit()
    db_session.add(MentorProfile(user_id=mentor_user.id, is_approved=True))
    db_session.commit()

    request = student.post(
        "/students/me/mentorship-requests",
        json={"mentor_id": str(mentor_user.id), "message": "hi"},
    )
    assert request.status_code == 201
