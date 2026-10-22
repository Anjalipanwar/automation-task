import pytest

from framework.clients.products_client import ProductsClient
from framework.models.error import ErrorResponse
from framework.models.product import PaginatedProducts, Product
from framework.utils.data_factory import random_ulid


# Function scope: a cheap pick from the shared, module-scoped `product_list`.
# Shows a narrow fixture building on a wider one; no extra API call per test.
@pytest.fixture
def existing_product(product_list: list[Product]) -> Product:
    print("\n[SETUP function] existing_product: first item of product_list")
    return product_list[0]


# Parametrized fixture: pytest runs every test that uses it once per value in `params`.
# `request.param` holds the current value. Compare with @pytest.mark.parametrize below,
# where the values belong to one test; here they belong to the fixture, so any test
# that asks for `sort_option` gets all four variations automatically.
@pytest.fixture(
    params=["price,asc", "price,desc", "name,asc", "name,desc"],
    ids=["price-asc", "price-desc", "name-asc", "name-desc"],
)
def sort_option(request: pytest.FixtureRequest) -> str:
    print(f"\n[SETUP function] sort_option: {request.param}")
    return request.param


@pytest.mark.smoke
def test_list_products_returns_paginated_products(products_client: ProductsClient) -> None:
    response = products_client.list_products()

    assert response.status == 200, f"Expected 200, got {response.status}: {response.text()}"
    page = PaginatedProducts.model_validate(response.json())
    assert page.current_page == 1
    assert 0 < len(page.data) <= page.per_page


@pytest.mark.regression
def test_get_product_by_id_returns_matching_product(
    products_client: ProductsClient, existing_product: Product
) -> None:
    response = products_client.get_product(existing_product.id)

    assert response.status == 200, f"Expected 200, got {response.status}: {response.text()}"
    product = Product.model_validate(response.json())
    assert product.id == existing_product.id
    assert product.name == existing_product.name
    assert product.price == existing_product.price
    assert product.brand.id == existing_product.brand.id
    assert product.category.id == existing_product.category.id


@pytest.mark.regression
def test_get_product_with_unknown_id_returns_404(products_client: ProductsClient) -> None:
    response = products_client.get_product(random_ulid())

    assert response.status == 404, f"Expected 404, got {response.status}: {response.text()}"
    error = ErrorResponse.model_validate(response.json())
    assert error.message == "Requested item not found"


@pytest.mark.regression
def test_list_products_filtered_by_category_returns_only_that_category(
    products_client: ProductsClient, existing_product: Product
) -> None:
    category_id = existing_product.category.id

    response = products_client.list_products(params={"by_category": category_id})

    assert response.status == 200, f"Expected 200, got {response.status}: {response.text()}"
    page = PaginatedProducts.model_validate(response.json())
    assert page.data, f"No products returned for category {category_id}"
    assert all(p.category.id == category_id for p in page.data)


# @pytest.mark.parametrize: the values belong to this one test. pytest generates
# one test per tuple; `ids` gives each case a readable name in the output.
@pytest.mark.regression
@pytest.mark.parametrize(
    "search_term",
    ["pliers", "hammer", "saw", "HAMMER"],
    ids=["pliers", "hammer", "saw", "uppercase-is-case-insensitive"],
)
def test_search_products_returns_only_matching_names(
    products_client: ProductsClient, search_term: str
) -> None:
    response = products_client.search_products(search_term)

    assert response.status == 200, f"Expected 200, got {response.status}: {response.text()}"
    page = PaginatedProducts.model_validate(response.json())
    assert page.data, f"No products found for '{search_term}'"
    assert all(search_term.lower() in p.name.lower() for p in page.data)


# Uses the parametrized fixture `sort_option`, so this one test runs four times.
@pytest.mark.regression
def test_list_products_is_sorted_by_requested_option(
    products_client: ProductsClient, sort_option: str
) -> None:
    field, direction = sort_option.split(",")

    response = products_client.list_products(params={"sort": sort_option})

    assert response.status == 200, f"Expected 200, got {response.status}: {response.text()}"
    page = PaginatedProducts.model_validate(response.json())
    values = [getattr(p, field) for p in page.data]
    sort_key = str.casefold if field == "name" else None
    assert values == sorted(values, key=sort_key, reverse=direction == "desc")
