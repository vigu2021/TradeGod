from typing import ClassVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class PublicModel(BaseModel):
    """Base for all public-facing API schemas.

    - Auto-generates camelCase aliases for JSON in/out (matches JS conventions)
    - Accepts either camelCase or snake_case on input
    - Converts from ORM objects via attribute access
    - Always serializes with aliases so responses come out in camelCase
    """

    model_config: ClassVar[ConfigDict] = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
        ser_json_by_alias=True,  # pyright: ignore[reportCallIssue]
    )
