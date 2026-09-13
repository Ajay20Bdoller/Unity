from pydantic import BaseModel


class LoginRequest(BaseModel):
    identifier: str  # email or mobile number
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
