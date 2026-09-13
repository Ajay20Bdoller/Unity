STUDENT_PAYLOAD = {
    "full_name": "Forgot Password Student",
    "role": "student",
    "mobile_number": "9800000001",
    "password": "OldPass123!",
    "date_of_birth": "2010-01-01",
    "school_name": "School",
    "parent_name": "Parent",
    "parent_relation": "Mother",
    "address": "addr",
    "district": "d",
    "state": "Delhi",
}


def test_unregistered_mobile_gets_generic_response_no_otp(client):
    res = client.post(
        "/auth/forgot-password/request-otp", json={"mobile_number": "0000000000"}
    )
    assert res.status_code == 200
    body = res.json()
    assert body["dev_otp"] is None
    assert "registered" in body["message"].lower()


def test_full_reset_flow_and_old_password_stops_working(client):
    client.post("/auth/register", json=STUDENT_PAYLOAD)

    otp_response = client.post(
        "/auth/forgot-password/request-otp", json={"mobile_number": "9800000001"}
    )
    assert otp_response.status_code == 200
    otp = otp_response.json()["dev_otp"]
    assert otp is not None

    wrong = client.post(
        "/auth/forgot-password/reset",
        json={"mobile_number": "9800000001", "otp": "000000", "new_password": "NewPass123!"},
    )
    assert wrong.status_code == 400

    reset = client.post(
        "/auth/forgot-password/reset",
        json={"mobile_number": "9800000001", "otp": otp, "new_password": "NewPass123!"},
    )
    assert reset.status_code == 204

    old_login = client.post(
        "/auth/login", json={"identifier": "9800000001", "password": "OldPass123!"}
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/auth/login", json={"identifier": "9800000001", "password": "NewPass123!"}
    )
    assert new_login.status_code == 200

    # the same OTP can't be replayed for a second reset
    replay = client.post(
        "/auth/forgot-password/reset",
        json={"mobile_number": "9800000001", "otp": otp, "new_password": "AnotherPass123!"},
    )
    assert replay.status_code == 400


def test_reset_revokes_other_active_sessions(client):
    client.post("/auth/register", json={**STUDENT_PAYLOAD, "mobile_number": "9800000002"})
    login = client.post(
        "/auth/login", json={"identifier": "9800000002", "password": "OldPass123!"}
    )
    assert login.status_code == 200

    otp = client.post(
        "/auth/forgot-password/request-otp", json={"mobile_number": "9800000002"}
    ).json()["dev_otp"]
    client.post(
        "/auth/forgot-password/reset",
        json={"mobile_number": "9800000002", "otp": otp, "new_password": "NewPass123!"},
    )

    # the refresh_token cookie from the pre-reset login is now revoked
    refresh_after_reset = client.post("/auth/refresh")
    assert refresh_after_reset.status_code == 401
