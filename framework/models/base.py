from pydantic import BaseModel, ConfigDict


class ApiModel(BaseModel):
    """Base for response models. Strict mode rejects type coercion (e.g. "1" for a bool)."""

    model_config = ConfigDict(strict=True)
