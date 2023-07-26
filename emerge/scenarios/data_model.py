""" Module for handling data model used in scenario generation. """


from typing import List, Optional
from enum import Enum

# pylint: disable=no-name-in-module
from pydantic import BaseModel, confloat, conint, Field

# pylint: disable=too-few-public-methods


class CustomerModel(BaseModel):
    """Interface for representing customer used in pv scenario development."""

    name: str
    kw: float
    distance: float
    cust_type: Optional[str]


class CapacityStrategyEnum(str, Enum):
    """Available strategies for sizing solar systems."""

    # pylint: disable=invalid-name
    default = "default"
    peakmultiplier = "peakmultiplier"


class SelectionStrategyEnum(str, Enum):
    """Available strategies for selecting loads to have pv system."""

    # pylint: disable=invalid-name
    random_allocation = "random_allocation"
    far_allocation = "far_allocation"
    near_allocation = "near_allocation"


class DefaultCapacityStrategyInput(BaseModel):
    """Input model for default solar sizing strategy."""

    capacity_factor: confloat(gt=0, le=1) = 0.3
    load_factor: confloat(gt=0, le=1) = 0.33
    max_pct_production: confloat(gt=0, le=500) = 100


class PeakMultiplierCapacityStrategyInput(BaseModel):
    """Input model for peak multiplier capacity sizing strategy."""

    multiplier: float = 1


class PVScenarioConfig(BaseModel):
    """Basic input model for generating solar scenarios."""

    pct_resolution: confloat(gt=0, le=100) = Field(
        description="Percentage resolution or step resolution"
    )
    num_of_penetration: conint(gt=0)
    max_num_of_samples: conint(ge=1) = 1


class PVModel(BaseModel):
    """Basic solar model used in solar scenario development."""

    name: str
    kw: confloat(ge=0)
    customer: str


class DistPVScenarioModel(BaseModel):
    """Model for storing solars in a given scenario."""

    name: str
    sample_id: int
    pv_penetration: float
    pvs: List[PVModel]


class LoadMetadataModel(BaseModel):
    """Interface for representing OpenDSS load metadata."""

    name: str
    bus: str
    num_phase: conint(ge=1, le=3)
    kv: confloat(gt=0)
    yearly: Optional[str]
