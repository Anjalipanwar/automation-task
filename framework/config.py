"""Loads test settings from environment variables (and a local .env file)."""

import os
from functools import lru_cache

from dotenv import load_dotenv
from pydantic import BaseModel, HttpUrl


class Settings(BaseModel):
    base_url: HttpUrl
    api_token: str | None = None
    timeout_ms: float = 30_000
    # Admin account, needed for endpoints that require auth (e.g. DELETE /brands/{id})
    admin_email: str | None = None
    admin_password: str | None = None


@lru_cache
def get_settings() -> Settings:
    load_dotenv()
    base_url = os.getenv("BASE_URL")
    if not base_url:
        raise RuntimeError("BASE_URL is not set. Copy .env.example to .env and fill it in.")
    return Settings(
        base_url=base_url,
        api_token=os.getenv("API_TOKEN") or None,
        timeout_ms=float(os.getenv("TIMEOUT_MS", "30000")),
        admin_email=os.getenv("ADMIN_EMAIL") or None,
        admin_password=os.getenv("ADMIN_PASSWORD") or None,
    )
