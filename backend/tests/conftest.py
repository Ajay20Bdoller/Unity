import os

# Settings() requires these at import time. Tests that don't touch a real
# database only need config to load, not a live connection — set harmless
# defaults so `pytest` works out of the box with no .env file.
os.environ.setdefault("DATABASE_URL", "postgresql://user:password@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
