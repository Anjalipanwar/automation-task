"""Product models, based on the Swagger schemas at /api/documentation.

The spec marks no fields as required. Fields are required here when the live API always
returns them; fields it only returns sometimes are optional.
"""

from pydantic import Field

from framework.models.base import ApiModel
from framework.models.brand import Brand


class Category(ApiModel):
    """Swagger: CategoryResponse.

    `parent_id` is only returned by GET /products/{id}; `slug` is missing from GET /products/search.
    """

    id: str
    name: str
    slug: str | None = None
    parent_id: str | None = None
    sub_categories: list["Category"] = Field(default_factory=list)


class ProductImage(ApiModel):
    """Swagger: ImageResponse."""

    id: str
    by_name: str
    by_url: str
    source_name: str
    source_url: str
    file_name: str
    title: str


class ProductSpec(ApiModel):
    """Swagger: ProductSpecResponse."""

    id: str
    product_id: str
    spec_name: str
    spec_value: str
    spec_unit: str | None


class Product(ApiModel):
    """Swagger: ProductResponse."""

    id: str
    name: str
    description: str
    price: float
    is_location_offer: bool
    is_rental: bool
    in_stock: bool
    co2_rating: str
    is_eco_friendly: bool
    brand: Brand
    category: Category
    product_image: ProductImage
    # Only returned by GET /products/{id}
    specs: list[ProductSpec] | None = None


class PaginatedProducts(ApiModel):
    """Swagger: PaginatedProductResponse (response of GET /products)."""

    current_page: int
    data: list[Product]
    # "from"/"to" are null when the page is empty
    from_: int | None = Field(alias="from")
    to: int | None
    last_page: int
    per_page: int
    total: int
