""" Module for managing pydantic data models."""

from pydantic import BaseModel, confloat


class ThermalLoadingLimit(BaseModel):
    """ Model representing thermal loading limit. """

    threshold: confloat(ge = 0.0, le=2.0) = 1.0

class VoltageViolationLimit(BaseModel):
    """ Model representing voltage violation limit. """

    overvoltage_threshold: confloat(ge = 1.01, le=2.0) = 1.05
    undervoltage_threshold: confloat(ge = 0, le=1.0) = 0.95