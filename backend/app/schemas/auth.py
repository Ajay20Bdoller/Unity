from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    identifier: str  # email or mobile number
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    mobile_number: str


class ForgotPasswordOTPResponse(BaseModel):
    message: str
    dev_otp: str | None = None  # only populated when ENVIRONMENT=development


class ResetPasswordRequest(BaseModel):
    mobile_number: str
    otp: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return value


class GoogleAuthConfig(BaseModel):
    enabled: bool
    client_id: str | None = None


class GoogleAuthRequest(BaseModel):
    id_token: str


class GoogleAuthResponse(BaseModel):
    # "logged_in": an account (existing, or newly linked by matching
    # email) was found and the user is now authenticated -- cookies are
    # already set by this response.
    # "new_user": no account exists yet. The frontend should send the
    # person into registration with google_id/email/full_name
    # pre-filled; they still pick a role and fill in the fields Google
    # doesn't provide (mobile number, and everything role-specific).
    status: str
    access_token: str | None = None
    google_id: str | None = None
    email: str | None = None
    full_name: str | None = None
