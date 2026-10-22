"""Shared fixtures, grouped by scope (widest first).

Execution order rule of thumb:
  - Wider scopes are set up first: session -> module -> function.
  - Within the same scope, autouse fixtures run before the ones a test asks for.
  - Teardown (code after `yield`) runs in reverse order, and always runs,
    even when the test fails.
"""

from collections.abc import Generator

import pytest
from playwright.sync_api import APIRequestContext, Playwright

from framework.clients.auth_client import AuthClient
from framework.clients.brands_client import BrandsClient
from framework.clients.products_client import ProductsClient
from framework.config import Settings, get_settings
from framework.models.auth import TokenResponse
from framework.models.brand import Brand
from framework.models.product import PaginatedProducts, Product
from framework.utils.data_factory import build_brand_payload


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "smoke: quick checks of critical endpoints")
    config.addinivalue_line("markers", "regression: full regression suite")


# ---------------------------------------------------------------------------
# Session scope: created once for the whole test run, shared by every test.
# ---------------------------------------------------------------------------


# Session scope: settings come from .env and don't change during a run.
@pytest.fixture(scope="session")
def settings() -> Settings:
    print("\n[SETUP session] settings")
    return get_settings()


# Session scope: opening an HTTP context is relatively costly and it holds no
# per-test state, so one context is reused by all tests. Disposed at the very end.
@pytest.fixture(scope="session")
def api_request_context(
    playwright: Playwright, settings: Settings
) -> Generator[APIRequestContext]:
    print("\n[SETUP session] api_request_context")
    headers = {"Accept": "application/json"}
    if settings.api_token:
        headers["Authorization"] = f"Bearer {settings.api_token}"

    # Trailing slash so relative paths like "products/1" are joined onto the base path.
    base_url = str(settings.base_url).rstrip("/") + "/"
    context = playwright.request.new_context(
        base_url=base_url,
        extra_http_headers=headers,
        timeout=settings.timeout_ms,
    )
    yield context
    print("\n[TEARDOWN session] api_request_context: disposing")
    context.dispose()


# Session scope: clients are stateless wrappers. They must be at least as wide
# as any fixture that uses them; the module-scoped `product_list` below needs
# `products_client`, and pytest forbids a wider fixture depending on a narrower one.
@pytest.fixture(scope="session")
def products_client(api_request_context: APIRequestContext) -> ProductsClient:
    print("\n[SETUP session] products_client")
    return ProductsClient(api_request_context)


# Session scope: same reasoning as products_client.
@pytest.fixture(scope="session")
def brands_client(api_request_context: APIRequestContext) -> BrandsClient:
    print("\n[SETUP session] brands_client")
    return BrandsClient(api_request_context)


# Session scope: log in once and reuse the token, instead of logging in for
# every test. (Tokens last 5 minutes, which is plenty for this suite.)
# Skips dependent tests if credentials are not configured in .env.
@pytest.fixture(scope="session")
def admin_token(api_request_context: APIRequestContext, settings: Settings) -> str:
    print("\n[SETUP session] admin_token: logging in")
    if not (settings.admin_email and settings.admin_password):
        pytest.skip("ADMIN_EMAIL / ADMIN_PASSWORD not set (.env locally, secrets in CI)")
    response = AuthClient(api_request_context).login(
        settings.admin_email, settings.admin_password
    )
    assert response.status == 200, f"Login failed: {response.status} {response.text()}"
    return TokenResponse.model_validate(response.json()).access_token


# ---------------------------------------------------------------------------
# Module scope: created once per test file that uses it.
# ---------------------------------------------------------------------------


# Module scope: the product list doesn't change while tests run, so fetch it
# once per test file and let every test in that file share the result.
# A test file that never asks for it never triggers the request.
@pytest.fixture(scope="module")
def product_list(products_client: ProductsClient) -> Generator[list[Product]]:
    print("\n[SETUP module] product_list: GET /products")
    response = products_client.list_products()
    assert response.ok, f"Could not list products: {response.status} {response.text()}"
    products = PaginatedProducts.model_validate(response.json()).data
    assert products, "GET /products returned no products to test with"
    yield products
    print("\n[TEARDOWN module] product_list")


# ---------------------------------------------------------------------------
# Function scope: created fresh for every single test (the default scope).
# ---------------------------------------------------------------------------


# Function scope + autouse: runs around every test automatically, without the
# test asking for it. Handy for logging, timing, or resetting state.
@pytest.fixture(autouse=True)
def log_test_name(request: pytest.FixtureRequest) -> Generator[None]:
    print(f"\n[SETUP function] log_test_name: START {request.node.name}")
    yield
    print(f"\n[TEARDOWN function] log_test_name: END {request.node.name}")


# Function scope: each test gets its own brand, so tests can't interfere with
# each other. Setup creates it through the API; teardown deletes it.
# The code after `yield` runs even if the test fails, so no data is left behind.
# `admin_token` is requested up front, so if login fails or is skipped we
# never create a brand we couldn't delete.
@pytest.fixture
def created_brand(brands_client: BrandsClient, admin_token: str) -> Generator[Brand]:
    response = brands_client.create_brand(build_brand_payload())
    assert response.status == 201, f"Create failed: {response.status} {response.text()}"
    brand = Brand.model_validate(response.json())
    print(f"\n[SETUP function] created_brand: created {brand.id} ({brand.name})")

    yield brand

    response = brands_client.delete_brand(brand.id, token=admin_token)
    print(f"\n[TEARDOWN function] created_brand: deleted {brand.id} -> {response.status}")
    # 404 is fine: the test itself may already have deleted it.
    assert response.status in (204, 404), f"Cleanup failed: {response.status} {response.text()}"
