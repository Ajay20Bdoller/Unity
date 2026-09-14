"""verify_oauth2_token itself (the cryptographic verification against
Google's public keys) can't be exercised here -- it requires real
network access to Google and a genuinely Google-issued token, neither
of which this environment has. These tests monkeypatch that one call
to simulate what a verified response looks like, so what's actually
under test is this endpoint's own logic: finding an existing linked
account, linking by matching email, and reporting "new_user" correctly
-- not Google's cryptography, which is Google's library's job to get
right, not this codebase's.
"""

import app.api.routes.auth as auth_module


def _fake_google_response(sub, email, name="Test User", email_verified=True):
    def fake_verify(*args, **kwargs):
        return {"sub": sub, "email": email, "name": name, "email_verified": email_verified}

    return fake_verify


def test_config_reports_disabled_without_client_id(client):
    res = client.get("/auth/google/config")
    assert res.status_code == 200
    assert res.json() == {"enabled": False, "client_id": None}


def test_returns_503_when_not_configured(client):
    res = client.post("/auth/google", json={"id_token": "whatever"})
    assert res.status_code == 503


def test_new_user_reports_correctly(client, monkeypatch):
    monkeypatch.setattr(auth_module.settings, "GOOGLE_CLIENT_ID", "fake-client-id")
    monkeypatch.setattr(
        auth_module.google_id_token,
        "verify_oauth2_token",
        _fake_google_response("google-sub-new-1", "brandnew@example.com", "Brand New"),
    )

    res = client.post("/auth/google", json={"id_token": "fake"})
    assert res.status_code == 200
    body = res.json()
    assert body["status"] == "new_user"
    assert body["google_id"] == "google-sub-new-1"
    assert body["email"] == "brandnew@example.com"
    assert body["full_name"] == "Brand New"


def test_unverified_email_rejected(client, monkeypatch):
    monkeypatch.setattr(auth_module.settings, "GOOGLE_CLIENT_ID", "fake-client-id")
    monkeypatch.setattr(
        auth_module.google_id_token,
        "verify_oauth2_token",
        _fake_google_response("google-sub-2", "unverified@example.com", email_verified=False),
    )

    res = client.post("/auth/google", json={"id_token": "fake"})
    assert res.status_code == 401


def test_existing_google_linked_account_logs_in(client, monkeypatch):
    monkeypatch.setattr(auth_module.settings, "GOOGLE_CLIENT_ID", "fake-client-id")

    # First call: brand new -> register normally with the google_id
    # the "new_user" response would have carried through.
    monkeypatch.setattr(
        auth_module.google_id_token,
        "verify_oauth2_token",
        _fake_google_response("google-sub-3", "linked@example.com", "Linked User"),
    )
    client.post("/auth/google", json={"id_token": "fake"})
    reg = client.post(
        "/auth/register",
        json={
            "full_name": "Linked User",
            "role": "mentor",
            "email": "linked@example.com",
            "mobile_number": "9970000010",
            "password": "TestPass123!",
            "date_of_birth": "1990-01-01",
            "google_id": "google-sub-3",
        },
    )
    assert reg.status_code == 201

    # Second call, same google sub: should now log in directly.
    res = client.post("/auth/google", json={"id_token": "fake-2"})
    assert res.status_code == 200
    assert res.json()["status"] == "logged_in"

    me = client.get("/auth/me")
    assert me.status_code == 200
    assert me.json()["email"] == "linked@example.com"


def test_existing_email_gets_linked_not_duplicated(client, admin_client, monkeypatch):
    monkeypatch.setattr(auth_module.settings, "GOOGLE_CLIENT_ID", "fake-client-id")

    client.post(
        "/auth/register",
        json={
            "full_name": "Password User",
            "role": "mentor",
            "email": "passworduser@example.com",
            "mobile_number": "9970000011",
            "password": "TestPass123!",
            "date_of_birth": "1990-01-01",
        },
    )

    monkeypatch.setattr(
        auth_module.google_id_token,
        "verify_oauth2_token",
        _fake_google_response("google-sub-4", "passworduser@example.com", "Password User"),
    )
    res = client.post("/auth/google", json={"id_token": "fake"})
    assert res.status_code == 200
    assert res.json()["status"] == "logged_in"

    all_mentors = admin_client.get("/admin/mentors").json()
    matches = [m for m in all_mentors if m["email"] == "passworduser@example.com"]
    assert len(matches) == 1  # linked to the existing account, not duplicated
