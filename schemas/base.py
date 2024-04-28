from enum import Enum
from pydantic import BaseModel, ConfigDict


class GeneralModel(BaseModel):
    model_config = ConfigDict(
        extra="ignore",
        use_enum_values=True,
        from_attributes=True,
        validate_assignment=True,
        populate_by_name=True,
        coerce_numbers_to_str=True,
    )
