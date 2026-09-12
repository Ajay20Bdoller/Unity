from datetime import datetime, timezone

from app.core.security import (
    create_access_token,
    decode_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)


def test_hash_password_roundtrip():
    hashed = hash_password("CorrectHorseBatteryStaple")
    assert hashed != "CorrectHorseBatteryStaple"
    assert verify_password("CorrectHorseBatteryStaple", hashed)


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("CorrectHorseBatteryStaple")
    assert not verify_password("WrongPassword", hashed)


def test_hash_password_handles_long_password():
    """Regression test.

    bcrypt 5.x + passlib 1.7.4 crashed on passwords near/over 72 bytes
    instead of truncating, breaking /auth/register with a 500. Pinning
    bcrypt==4.0.1 in requirements.txt fixes this — this test guards
    against a silent re-break if that pin is ever loosened.
    """
    long_password = "a" * 100
    hashed = hash_password(long_password)
    assert verify_password(long_password, hashed)


def test_access_token_roundtrip():
    token = create_access_token(subject="user-123", extra_claims={"role": "student"})
    payload = decode_access_token(token)
    assert payload is not None
    assert payload["sub"] == "user-123"
    assert payload["role"] == "student"


def test_decode_access_token_rejects_garbage():
    assert decode_access_token("not-a-real-token") is None


def test_refresh_token_is_high_entropy_and_unique():
    a, b = generate_refresh_token(), generate_refresh_token()
    assert a != b
    assert len(a) > 40  # secrets.token_urlsafe(48) — plenty of entropy


def test_refresh_token_hash_is_deterministic_and_not_reversible():
    raw = generate_refresh_token()
    h1, h2 = hash_refresh_token(raw), hash_refresh_token(raw)
    assert h1 == h2  # same input -> same hash, needed to look it up in the DB
    assert h1 != raw
    assert len(h1) == 64  # sha256 hex digest


def test_refresh_token_expiry_is_in_the_future():
    assert refresh_token_expiry() > datetime.now(timezone.utc)
