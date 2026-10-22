from framework.models.base import ApiModel


class ErrorResponse(ApiModel):
    """Swagger: ItemNotFoundResponse."""

    message: str
