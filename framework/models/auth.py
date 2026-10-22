from framework.models.base import ApiModel


class TokenResponse(ApiModel):
    """Swagger: TokenResponse (response of POST /users/login)."""

    access_token: str
    token_type: str
    expires_in: float
