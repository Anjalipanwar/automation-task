from typing import Any

from playwright.sync_api import APIResponse

from framework.clients.base_client import BaseClient


class ProductsClient(BaseClient):
    RESOURCE = "products"

    def list_products(self, params: dict[str, Any] | None = None) -> APIResponse:
        """GET /products. Supported params: by_brand, by_category, is_rental, between, sort, page."""
        return self.get(self.RESOURCE, params=params)

    def get_product(self, product_id: str) -> APIResponse:
        """GET /products/{productId}."""
        return self.get(f"{self.RESOURCE}/{product_id}")

    def search_products(self, query: str) -> APIResponse:
        """GET /products/search?q=... Returns the same paginated shape as GET /products."""
        return self.get(f"{self.RESOURCE}/search", params={"q": query})
