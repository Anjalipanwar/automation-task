from framework.models.base import ApiModel


class Brand(ApiModel):
    """Swagger: BrandResponse. `slug` is not returned when nested in a product."""

    id: str
    name: str
    slug: str | None = None
