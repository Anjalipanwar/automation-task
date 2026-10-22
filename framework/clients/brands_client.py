from typing import Any

from playwright.sync_api import APIResponse

from framework.clients.base_client import BaseClient


class BrandsClient(BaseClient):
    RESOURCE = "brands"

    def create_brand(self, payload: dict[str, Any]) -> APIResponse:
        """POST /brands (no auth needed). Payload: name, slug."""
        return self.post(self.RESOURCE, data=payload)

    def get_brand(self, brand_id: str) -> APIResponse:
        """GET /brands/{brandId}."""
        return self.get(f"{self.RESOURCE}/{brand_id}")

    def delete_brand(self, brand_id: str, token: str | None = None) -> APIResponse:
        """DELETE /brands/{brandId}. Needs an admin token; without one the API returns 401."""
        headers = self.bearer(token) if token else None
        return self.delete(f"{self.RESOURCE}/{brand_id}", headers=headers)
