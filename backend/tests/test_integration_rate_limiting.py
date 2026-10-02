"""These import the limiter instances directly to shrink them for the
duration of a single test (rather than sending hundreds of requests to
hit the real production limits), then restore them -- the autouse
_reset_rate_limiters fixture in conftest.py clears state but doesn't
change max_requests/window_seconds, so that's this file's job.
"""

from app.api.routes.auth import _login_limiter, _register_limiter


def test_google_auth_shares_the_login_limiter(client):
    """Found missing entirely during a deployment audit -- POST /auth/
    google had no rate limit at all, unlike every other auth endpoint,
    despite triggering an outbound network call to Google on every
    request (making it a cheaper resource-exhaustion vector than even
    password login). This just confirms the limiter check actually
    fires on this route; the token itself doesn't need to be valid for
    that, since the limiter check runs before any Google verification.
    """
    original_max = _login_limiter.max_requests
    _login_limiter.max_requests = 3
    try:
        for _ in range(3):
            res = client.post("/auth/google", json={"id_token": "whatever"})
            assert res.status_code in (401, 503)  # not configured / bad token, but under budget

        blocked = client.post("/auth/google", json={"id_token": "whatever"})
        assert blocked.status_code == 429
    finally:
        _login_limiter.max_requests = original_max


def test_login_blocked_after_too_many_attempts(client):
    original_max = _login_limiter.max_requests
    _login_limiter.max_requests = 3
    try:
        for _ in range(3):
            res = client.post(
                "/auth/login", json={"identifier": "9990000000", "password": "wrong"}
            )
            assert res.status_code == 401  # wrong credentials, but under the limit

        blocked = client.post(
            "/auth/login", json={"identifier": "9990000000", "password": "wrong"}
        )
        assert blocked.status_code == 429
    finally:
        _login_limiter.max_requests = original_max


def test_register_blocked_after_too_many_attempts(client):
    original_max = _register_limiter.max_requests
    _register_limiter.max_requests = 2
    try:
        for i in range(2):
            res = client.post(
                "/auth/register",
                json={
                    "full_name": f"Rate Limited {i}",
                    "role": "student",
                    "mobile_number": f"999100000{i}",
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
            assert res.status_code == 201

        blocked = client.post(
            "/auth/register",
            json={
                "full_name": "One Too Many",
                "role": "student",
                "mobile_number": "9991000099",
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
        assert blocked.status_code == 429
    finally:
        _register_limiter.max_requests = original_max
