"""TestClient (like curl) doesn't enforce SameSite policy, so it can't
catch the underlying browser bug itself -- but it can and should verify
the actual Set-Cookie header content is correct, which is what a real
browser reads to decide whether to attach cookies to cross-site API
calls at all.
"""

import app.api.routes.auth as auth_module


def _register_and_login(client, mobile):
    client.post(
        "/auth/register",
        json={
            "full_name": "Cookie Test",
            "role": "student",
            "mobile_number": mobile,
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
    return client.post("/auth/login", json={"identifier": mobile, "password": "TestPass123!"})


def test_production_cookies_use_samesite_none_and_secure(client, monkeypatch):
    # auth.py reads settings.ENVIRONMENT fresh on every request (not
    # cached at import time), so mutating the already-constructed
    # settings singleton's attribute directly is enough -- no need to
    # clear get_settings()'s lru_cache or reload any modules.
    monkeypatch.setattr(auth_module.settings, "ENVIRONMENT", "production")

    res = _register_and_login(client, "9930000001")
    cookie_headers = res.headers.get_list("set-cookie")
    assert any("SameSite=none" in h and "Secure" in h for h in cookie_headers), cookie_headers


def test_dev_cookies_use_samesite_lax_without_secure(client):
    res = _register_and_login(client, "9930000002")
    cookie_headers = res.headers.get_list("set-cookie")
    assert any("SameSite=lax" in h for h in cookie_headers), cookie_headers
    assert not any("Secure" in h for h in cookie_headers), cookie_headers
