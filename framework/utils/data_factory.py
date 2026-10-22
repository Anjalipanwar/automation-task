"""Faker-based test data helpers."""

from typing import Any

from faker import Faker

fake = Faker()

# Crockford base32, the alphabet used by ULIDs (the API's id format)
_ULID_CHARS = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"


def random_ulid() -> str:
    """A random, well-formed ULID. Useful as an id that does not exist."""
    return fake.lexify("?" * 26, letters=_ULID_CHARS)


def build_brand_payload(**overrides: Any) -> dict[str, Any]:
    """A unique brand for POST /brands. The random suffix avoids slug clashes on the shared API."""
    suffix = fake.lexify("????????", letters="abcdefghijklmnopqrstuvwxyz0123456789")
    payload = {"name": f"Test Brand {suffix}", "slug": f"test-brand-{suffix}"}
    payload.update(overrides)
    return payload
