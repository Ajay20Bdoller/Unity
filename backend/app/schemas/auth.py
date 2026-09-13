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
