from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    ENVIRONMENT: str = "development"
    # "Sign in with Google" (Google Identity Services popup flow) --
    # only the Client ID is needed server-side, not a client secret:
    # the frontend gets a signed ID token directly from Google, and the
    # backend just verifies its signature/audience against this ID.
    # Get one at https://console.cloud.google.com/apis/credentials
    # (OAuth 2.0 Client ID, type "Web application", with your frontend
    # origin under "Authorized JavaScript origins"). Leave unset to
    # disable Google sign-in entirely -- GET /auth/google/config
    # reports whether it's configured so the frontend can hide the
    # button rather than show one that 400s.
    GOOGLE_CLIENT_ID: str | None = None
    # Whether OTPs (password reset, guardian consent) are echoed back in
    # the API response instead of only being "sent" (no real SMS
    # provider is wired up yet — see CLAUDE.md). Deliberately NOT tied
    # to ENVIRONMENT: a pilot deployment needs ENVIRONMENT=production
    # for secure cookies, but may still need this on until a real SMS
    # provider exists. Defaults to matching ENVIRONMENT (on for
    # development, off otherwise) but can be overridden explicitly --
    # see EXPOSE_DEV_OTP below.
    EXPOSE_DEV_OTP: bool | None = None

    @property
    def expose_dev_otp(self) -> bool:
        if self.EXPOSE_DEV_OTP is not None:
            return self.EXPOSE_DEV_OTP
        return self.ENVIRONMENT == "development"

    DATABASE_URL: str

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 days
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    OTP_EXPIRE_MINUTES: int = 10
    OTP_MAX_ATTEMPTS: int = 5

    GROK_API_KEY: str = ""
    GROK_MODEL: str = "llama-3.3-70b-versatile"
    GROK_BASE_URL: str = "https://api.groq.com/openai/v1"
    AI_MAX_TOKENS: int = 500
    AI_TEMPERATURE: float = 0.4
    AI_REQUEST_TIMEOUT: int = 20
    AI_MAX_MESSAGE_LENGTH: int = 2000
    AI_RATE_LIMIT_PER_MINUTE: int = 10

    CORS_ORIGINS: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
