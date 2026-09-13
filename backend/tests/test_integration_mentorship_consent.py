"""The most business-logic-heavy flow in the app: a student can only
request mentorship once a parent has verified the guardian relationship
AND granted MENTORSHIP consent via OTP. Every step matters, so this
tests the whole chain rather than any piece in isolation.
"""

from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.main import app
from app.models.profiles import MentorProfile
from app.models.user import User, UserRole


def _register_student(client, mobile="9200000001"):
    payload = {
        "full_name": "Consent Flow Student",
        "role": "student",
        "mobile_number": mobile,
        "password": "TestPass123!",
        "date_of_birth": "2010-01-01",
        "school_name": "School",
        "parent_name": "Parent",
        "parent_relation": "Mother",
        "address": "addr",
        "district": "d",
        "state": "s",
    }
    client.post("/auth/register", json=payload)
    client.post("/auth/login", json={"identifier": mobile, "password": "TestPass123!"})


def _register_parent(client, email="consentflow-parent@example.com"):
    payload = {
        "full_name": "Consent Flow Parent",
        "role": "parent",
        "email": email,
        "mobile_number": "9200000002",
        "password": "TestPass123!",
        "student_name": "Consent Flow Student",
        "relation_to_student": "Mother",
    }
    client.post("/auth/register", json=payload)
    client.post("/auth/login", json={"identifier": email, "password": "TestPass123!"})


def test_mentorship_request_blocked_without_any_consent(student_client):
    res = student_client.post(
        "/students/me/mentorship-requests",
        json={"mentor_id": "00000000-0000-0000-0000-000000000000", "message": "hi"},
    )
    # Consent is checked before the mentor lookup, so this 403s even
    # with a nonsense mentor_id -- the point being verified is that the
    # gate itself fires with zero consent state at all.
    assert res.status_code == 403


def test_full_consent_to_mentorship_chain(client, db_session):
    # Three independent logged-in sessions can't share one TestClient
    # (cookies would clobber each other), so build them separately.
    student = TestClient(app)
    parent = TestClient(app)
    mentor = TestClient(app)

    _register_student(student)
    _register_parent(parent)

    mentor_user = User(
        email="consentflow-mentor@example.com",
        full_name="Consent Flow Mentor",
        role=UserRole.MENTOR,
        hashed_password=hash_password("TestPass123!"),
    )
    db_session.add(mentor_user)
    db_session.commit()
    db_session.add(MentorProfile(user_id=mentor_user.id))
    db_session.commit()
    mentor.post(
        "/auth/login",
        json={"identifier": "consentflow-mentor@example.com", "password": "TestPass123!"},
    )

    invite = student.post(
        "/students/me/guardians", json={"parent_email": "consentflow-parent@example.com"}
    )
    assert invite.status_code == 201
    relationship_id = invite.json()["id"]

    still_blocked = student.post(
        "/students/me/mentorship-requests",
        json={"mentor_id": str(mentor_user.id), "message": "help"},
    )
    assert still_blocked.status_code == 403

    verify = parent.post(f"/parents/me/guardians/{relationship_id}/verify")
    assert verify.status_code == 200

    otp_request = parent.post(
        f"/parents/me/guardians/{relationship_id}/consent/mentorship/request-otp"
    )
    assert otp_request.status_code == 200
    otp = otp_request.json()["dev_otp"]
    assert otp is not None

    wrong_otp = parent.post(
        f"/parents/me/guardians/{relationship_id}/consent/mentorship/verify-otp",
        json={"otp": "000000"},
    )
    assert wrong_otp.status_code == 400

    right_otp = parent.post(
        f"/parents/me/guardians/{relationship_id}/consent/mentorship/verify-otp",
        json={"otp": otp},
    )
    assert right_otp.status_code == 200
    assert right_otp.json()["status"] == "granted"

    request = student.post(
        "/students/me/mentorship-requests",
        json={"mentor_id": str(mentor_user.id), "message": "Can you help with tech careers?"},
    )
    assert request.status_code == 201

    incoming = mentor.get("/mentors/me/requests").json()
    assert len(incoming) == 1
    request_id = incoming[0]["id"]

    accept = mentor.post(f"/mentors/me/requests/{request_id}/accept")
    assert accept.status_code == 200

    double_accept = mentor.post(f"/mentors/me/requests/{request_id}/accept")
    assert double_accept.status_code == 400

    session = mentor.post(
        f"/mentors/me/requests/{request_id}/sessions", json={"notes": "intro call"}
    )
    assert session.status_code == 201
    session_id = session.json()["id"]

    complete = mentor.post(f"/mentorship-sessions/{session_id}/complete")
    assert complete.status_code == 200
    assert complete.json()["completed"] is True

    feedback = student.post(
        f"/mentorship-sessions/{session_id}/feedback", json={"rating": 5, "comments": "Great"}
    )
    assert feedback.status_code == 201

    duplicate_feedback = student.post(
        f"/mentorship-sessions/{session_id}/feedback", json={"rating": 4}
    )
    assert duplicate_feedback.status_code == 409
