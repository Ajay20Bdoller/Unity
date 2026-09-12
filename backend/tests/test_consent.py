from datetime import datetime, timezone

from app.core.consent import generate_otp, hash_otp, otp_expiry


def test_otp_is_six_digits():
    otp = generate_otp()
    assert len(otp) == 6
    assert otp.isdigit()


def test_otp_hash_is_deterministic_and_not_reversible():
    otp = generate_otp()
    h1, h2 = hash_otp(otp), hash_otp(otp)
    assert h1 == h2
    assert h1 != otp
    assert len(h1) == 64


def test_otp_expiry_is_in_the_future():
    assert otp_expiry() > datetime.now(timezone.utc)
