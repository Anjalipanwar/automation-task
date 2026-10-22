import pytest

from framework.clients.brands_client import BrandsClient
from framework.models.brand import Brand


# Each test below gets its own fresh brand from the `created_brand` fixture
# (conftest.py), which also deletes it after the test, pass or fail.


@pytest.mark.regression
def test_created_brand_can_be_fetched_by_id(
    brands_client: BrandsClient, created_brand: Brand
) -> None:
    response = brands_client.get_brand(created_brand.id)

    assert response.status == 200, f"Expected 200, got {response.status}: {response.text()}"
    brand = Brand.model_validate(response.json())
    assert brand == created_brand


@pytest.mark.regression
def test_delete_brand_without_token_returns_401(
    brands_client: BrandsClient, created_brand: Brand
) -> None:
    response = brands_client.delete_brand(created_brand.id)

    assert response.status == 401, f"Expected 401, got {response.status}: {response.text()}"
