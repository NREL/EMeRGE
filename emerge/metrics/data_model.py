""" Module for managing pydantic data models."""

from pydantic import Field, BaseModel
from typing_extensions import Annotated


class ThermalLoadingLimit(BaseModel):
    """ Model representing thermal loading limit. """

    threshold: Annotated[float, Field(ge = 0.0, le=2.0)] = 1.0

class VoltageViolationLimit(BaseModel):
    """ Model representing voltage violation limit. """

    overvoltage_threshold: Annotated[float, Field(ge = 1.01, le=2.0)] = 1.05
    undervoltage_threshold: Annotated[float, Field(ge = 0, le=1.0)] = 0.95