STUDENT_PAYLOAD = {
    "full_name": "Change Password Student",
    "role": "student",
    "mobile_number": "9960000001",
    "password": "OldPass123!",
    "date_of_birth": "2010-01-01",
    "school_name": "School",
    "parent_name": "Parent",
    "parent_relation": "Mother",
    "address": "addr",
    "district": "d",
    "state": "Delhi",
}


def test_wrong_current_password_rejected(client):
    client.post("/auth/register", json=STUDENT_PAYLOAD)
    client.post("/auth/login", json={"identifier": "9960000001", "password": "OldPass123!"})

    res = client.post(
        "/auth/change-password",
        json={"current_password": "WrongPassword1!", "new_password": "NewPass123!"},
    )
    assert res.status_code == 401


def test_change_password_updates_login_credentials(client):
    client.post("/auth/register", json={**STUDENT_PAYLOAD, "mobile_number": "9960000002"})
    client.post("/auth/login", json={"identifier": "9960000002", "password": "OldPass123!"})

    change = client.post(
        "/auth/change-password",
        json={"current_password": "OldPass123!", "new_password": "NewPass123!"},
    )
    assert change.status_code == 204

    old_login = client.post(
        "/auth/login", json={"identifier": "9960000002", "password": "OldPass123!"}
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login", json={"identifier": "9960000002", "password": "NewPass123!"}
    )
    assert new_login.status_code == 200


import time


def test_token_issued_before_password_change_is_rejected_even_if_not_cleared(client):
    """The actual security property this feature exists for: an access
    token obtained before a password change must stop working, not just
    the refresh token -- otherwise a stolen/leaked token would remain
    valid for the rest of its lifetime (now up to 7 days) regardless of
    the password change. Simulated by holding onto the same TestClient's
    cookies (which a real browser would have overwritten) across the
    password change.

    The comparison in get_current_user is intentionally whole-second
    granularity (a token issued in the exact same second as a password
    change is not rejected -- otherwise the extremely common register-
    then-immediately-log-in flow would randomly 401 depending on test/
    request timing, which is worse than a sub-one-second gap in the
    rare stolen-token case). The sleep here reflects the realistic
    threat this guards against: a token used some real time after the
    change, not the exact same instant.
    """
    client.post("/auth/register", json={**STUDENT_PAYLOAD, "mobile_number": "9960000003"})
    client.post("/auth/login", json={"identifier": "9960000003", "password": "OldPass123!"})

    pre_change_me = client.get("/auth/me")
    assert pre_change_me.status_code == 200

    stolen_access_token = client.cookies.get("access_token")
    assert stolen_access_token

    time.sleep(1.1)
    client.post(
        "/auth/change-password",
        json={"current_password": "OldPass123!", "new_password": "NewPass123!"},
    )

    client.cookies.set("access_token", stolen_access_token)
    replay_attempt = client.get("/auth/me")
    assert replay_attempt.status_code == 401


def test_forgot_password_reset_also_invalidates_prior_tokens(client):
    client.post("/auth/register", json={**STUDENT_PAYLOAD, "mobile_number": "9960000004"})
    client.post("/auth/login", json={"identifier": "9960000004", "password": "OldPass123!"})
    stolen_access_token = client.cookies.get("access_token")

    time.sleep(1.1)
    otp = client.post(
        "/auth/forgot-password/request-otp", json={"mobile_number": "9960000004"}
    ).json()["dev_otp"]
    client.post(
        "/auth/forgot-password/reset",
        json={"mobile_number": "9960000004", "otp": otp, "new_password": "NewPass123!"},
    )

    client.cookies.set("access_token", stolen_access_token)
    replay_attempt = client.get("/auth/me")
    assert replay_attempt.status_code == 401
