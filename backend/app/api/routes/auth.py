from datetime import datetime, timezone

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import get_settings
from app.core.consent import generate_otp, hash_otp, otp_expiry
from app.core.rate_limit import InMemoryRateLimiter, get_client_ip
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    refresh_token_expiry,
    verify_password,
)
from app.db.session import get_db
from app.models.campaign import Campaign, CampaignRegistration
from app.models.password_reset import PasswordResetRequest
from app.models.profiles import (
    MentorProfile,
    ParentProfile,
    SchoolAdminProfile,
    StudentProfile,
)
from app.models.refresh_token import RefreshToken
from app.models.user import SELF_REGISTERABLE_ROLES, User, UserRole
from app.schemas.auth import (
    ForgotPasswordOTPResponse,
    ForgotPasswordRequest,
    LoginRequest,
    ResetPasswordRequest,
    Token,
)
from app.schemas.user import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])

# Per-IP, not per-account — an attacker doesn't need a valid account to
# hammer these. Limits are on the generous side for real users (a
# family sharing a connection, someone fat-fingering their password a
# few times) while still cutting off scripted abuse.
_login_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=15 * 60)
_register_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60 * 60)
_forgot_password_limiter = InMemoryRateLimiter(max_requests=5, window_seconds=60 * 60)
settings = get_settings()

ACCESS_COOKIE_MAX_AGE = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
REFRESH_COOKIE_MAX_AGE = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60

# Each self-registerable role gets its profile row created inline in
# register() below, since the fields collected genuinely differ per
# role (see UserCreate) — a generic profile_model(user_id=...) lookup
# no longer fits once roles need different constructor arguments.


def _set_auth_cookies(response: Response, access_token: str, raw_refresh_token: str) -> None:
    is_prod = settings.ENVIRONMENT != "development"
    # SameSite=Lax cookies are NOT sent on cross-site fetch/XHR requests
    # (only top-level navigations) -- and a real deployment has the
    # frontend and backend on different domains (e.g. vercel.app and
    # railway.app), which browsers treat as cross-site regardless of
    # CORS being configured correctly. SameSite=None is required for
    # the browser to attach these cookies to those API calls at all;
    # browsers in turn require Secure whenever SameSite=None is set, so
    # this only applies when is_prod (https) is true -- in local dev
    # (http, no TLS) SameSite=None would be silently rejected by the
    # browser, so Lax is correct there instead (frontend/backend on
    # different localhost *ports* are still same-site, so Lax works).
    # curl-based testing never surfaces this: curl doesn't enforce
    # SameSite at all, so every "live curl verification" throughout
    # development kept passing regardless of this setting.
    samesite = "none" if is_prod else "lax"
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=is_prod,
        samesite=samesite,
        max_age=ACCESS_COOKIE_MAX_AGE,
    )
    response.set_cookie(
        key="refresh_token",
        value=raw_refresh_token,
        httponly=True,
        secure=is_prod,
        samesite=samesite,
        max_age=REFRESH_COOKIE_MAX_AGE,
        path="/auth",  # only sent back to auth endpoints, not every request
    )


def _clear_auth_cookies(response: Response) -> None:
    is_prod = settings.ENVIRONMENT != "development"
    samesite = "none" if is_prod else "lax"
    response.delete_cookie("access_token", secure=is_prod, samesite=samesite)
    response.delete_cookie("refresh_token", path="/auth", secure=is_prod, samesite=samesite)


def _issue_tokens(db: Session, user: User) -> tuple[str, str]:
    access_token = create_access_token(
        subject=str(user.id), extra_claims={"role": user.role.value}
    )

    raw_refresh_token = generate_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=hash_refresh_token(raw_refresh_token),
            expires_at=refresh_token_expiry(),
        )
    )
    db.commit()
    return access_token, raw_refresh_token


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, request: Request, db: Session = Depends(get_db)) -> User:
    _register_limiter.check(get_client_ip(request))
    if payload.role not in SELF_REGISTERABLE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This role cannot be self-registered",
        )

    if payload.email and db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email is already registered")
    if payload.mobile_number and db.query(User).filter(
        User.mobile_number == payload.mobile_number
    ).first():
        raise HTTPException(status_code=400, detail="Mobile number is already registered")

    user = User(
        email=payload.email,
        mobile_number=payload.mobile_number,
        full_name=payload.full_name,
        role=payload.role,
        preferred_language=payload.preferred_language,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.flush()  # assigns user.id without committing yet

    if payload.role == UserRole.STUDENT:
        db.add(
            StudentProfile(
                user_id=user.id,
                date_of_birth=payload.date_of_birth,
                school_name=payload.school_name,
                address=payload.address,
                district=payload.district,
                state=payload.state,
                country=payload.country,
                parent_name=payload.parent_name,
                parent_relation=payload.parent_relation,
            )
        )
    elif payload.role == UserRole.PARENT:
        db.add(
            ParentProfile(
                user_id=user.id,
                student_name=payload.student_name,
                relation_to_student=payload.relation_to_student,
            )
        )
    elif payload.role == UserRole.MENTOR:
        db.add(MentorProfile(user_id=user.id, date_of_birth=payload.date_of_birth))
    elif payload.role == UserRole.SCHOOL_ADMIN:
        db.add(
            SchoolAdminProfile(
                user_id=user.id,
                date_of_birth=payload.date_of_birth,
                school_name=payload.school_name,
                school_location=payload.school_location,
            )
        )

    # Acquisition tracking is best-effort: an unknown, inactive, or
    # absent campaign_key must never block account creation.
    if payload.campaign_key:
        campaign = (
            db.query(Campaign)
            .filter(Campaign.key == payload.campaign_key, Campaign.active.is_(True))
            .first()
        )
        if campaign:
            db.add(
                CampaignRegistration(
                    user_id=user.id, campaign_id=campaign.id, source=payload.source
                )
            )

    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(
    payload: LoginRequest, request: Request, response: Response, db: Session = Depends(get_db)
) -> Token:
    _login_limiter.check(get_client_ip(request))
    user = (
        db.query(User)
        .filter(or_(User.email == payload.identifier, User.mobile_number == payload.identifier))
        .first()
    )
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email/mobile number or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is inactive")

    access_token, raw_refresh_token = _issue_tokens(db, user)
    _set_auth_cookies(response, access_token, raw_refresh_token)
    return Token(access_token=access_token)


@router.post("/refresh", response_model=Token)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> Token:
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token"
    )
    if not refresh_token:
        raise invalid

    token_hash = hash_refresh_token(refresh_token)
    stored = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
    if not stored or stored.revoked_at is not None:
        raise invalid
    if stored.expires_at < datetime.now(timezone.utc):
        raise invalid

    user = db.get(User, stored.user_id)
    if not user or not user.is_active:
        raise invalid

    # Rotate on every use: revoke the presented token, issue a fresh pair.
    # A reused (already-rotated) refresh token is refused above because
    # its revoked_at is already set — this catches token theft/replay.
    stored.revoked_at = datetime.now(timezone.utc)
    db.add(stored)

    access_token, raw_refresh_token = _issue_tokens(db, user)
    _set_auth_cookies(response, access_token, raw_refresh_token)
    return Token(access_token=access_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
) -> None:
    if refresh_token:
        token_hash = hash_refresh_token(refresh_token)
        stored = db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first()
        if stored and stored.revoked_at is None:
            stored.revoked_at = datetime.now(timezone.utc)
            db.add(stored)
            db.commit()
    _clear_auth_cookies(response)


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/forgot-password/request-otp", response_model=ForgotPasswordOTPResponse)
def request_password_reset_otp(
    payload: ForgotPasswordRequest, request: Request, db: Session = Depends(get_db)
) -> ForgotPasswordOTPResponse:
    """Mobile number only — this platform's identifier for password
    reset, not email (see CLAUDE.md: email is optional for students).
    Always returns the same generic message whether or not the number
    is registered, so this can't be used to check which numbers have
    accounts; only populates dev_otp when a matching user actually
    exists AND we're in dev mode."""
    _forgot_password_limiter.check(get_client_ip(request))
    is_dev = settings.expose_dev_otp
    user = db.query(User).filter(User.mobile_number == payload.mobile_number).first()

    if not user:
        return ForgotPasswordOTPResponse(
            message="If this mobile number is registered, an OTP has been generated."
        )

    raw_otp = generate_otp()
    db.add(
        PasswordResetRequest(
            user_id=user.id,
            otp_hash=hash_otp(raw_otp),
            otp_expires_at=otp_expiry(),
        )
    )
    db.commit()

    return ForgotPasswordOTPResponse(
        message="If this mobile number is registered, an OTP has been generated.",
        dev_otp=raw_otp if is_dev else None,
    )


@router.post("/forgot-password/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)) -> None:
    invalid = HTTPException(status_code=400, detail="Invalid or expired OTP")

    user = db.query(User).filter(User.mobile_number == payload.mobile_number).first()
    if not user:
        raise invalid

    reset_request = (
        db.query(PasswordResetRequest)
        .filter(PasswordResetRequest.user_id == user.id, PasswordResetRequest.used.is_(False))
        .order_by(PasswordResetRequest.created_at.desc())
        .first()
    )
    if not reset_request:
        raise invalid
    if reset_request.otp_attempts >= settings.OTP_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Too many attempts — request a new OTP")
    if reset_request.otp_expires_at < datetime.now(timezone.utc):
        raise invalid
    if hash_otp(payload.otp) != reset_request.otp_hash:
        reset_request.otp_attempts += 1
        db.add(reset_request)
        db.commit()
        raise invalid

    user.hashed_password = hash_password(payload.new_password)
    reset_request.used = True
    db.add(user)
    db.add(reset_request)

    # A password reset is a credible signal the account may have been
    # compromised (that's often exactly why someone is resetting it) —
    # revoke every other active session rather than leaving them valid.
    active_refresh_tokens = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .all()
    )
    now = datetime.now(timezone.utc)
    for token in active_refresh_tokens:
        token.revoked_at = now
        db.add(token)

    db.commit()
