""" Module for handling data model used in scenario generation. """


from typing import List, Optional, Dict
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

class DERType(str, Enum):
    """Available der enum types."""
    # pylint: disable=invalid-name
    load = 'load'
    solar = 'solar'

class CapacityStrategyEnum(str, Enum):
    """Available strategies for sizing solar systems."""

    # pylint: disable=invalid-name
    solar_energy_based = "solar_energy_based"
    peak_multiplier = "peak_multiplier"
    fixed_sizing = "fixed_sizing"


class SelectionStrategyEnum(str, Enum):
    """Available strategies for selecting loads to have pv system."""

    # pylint: disable=invalid-name
    random_allocation = "random_allocation"
    far_allocation = "far_allocation"
    near_allocation = "near_allocation"


class EnergyBasedSolarSizingStrategyInput(BaseModel):
    """Input model for default solar sizing strategy."""

    capacity_factor: confloat(gt=0, le=1) = 0.3
    load_factor: confloat(gt=0, le=1) = 0.33
    max_pct_production: confloat(gt=0, le=500) = 100


class ScenarioConfig(BaseModel):
    """Basic input model for generating der scenarios."""

    pct_resolution: confloat(gt=0, le=100) = Field(
        description="Percentage resolution or step resolution"
    )
    num_of_penetration: conint(gt=0)
    max_num_of_samples: conint(ge=1) = 1


class _DERScenarioInput(BaseModel):
    """ Base input model for der scenarios. """
    sizing_strategy: CapacityStrategyEnum
    der_type: DERType
    energy_sizing_input:  Dict[str,EnergyBasedSolarSizingStrategyInput] | EnergyBasedSolarSizingStrategyInput | None = None
    peakmult_sizing_input: Dict[str,float] | float | None = None
    fixed_sizing_input: Dict[str, float] | float | None

class DERScenarioInput(_DERScenarioInput):
    """ Input model for der scenarios. """
    selection_strategy: SelectionStrategyEnum
    other_ders: List[_DERScenarioInput]


class BasicDERModel(BaseModel):
    """Basic DER model used in solar scenario development."""

    name: str
    kw: confloat(ge=0)
    customer: CustomerModel
    der_type: DERType

class DistDERScenarioModel(BaseModel):
    """Model for storing solars in a given scenario."""

    name: str
    sample_id: int
    penetration: float
    ders: List[BasicDERModel]


class LoadMetadataModel(BaseModel):
    """Interface for representing OpenDSS load metadata."""

    name: str
    bus: str
    num_phase: conint(ge=1, le=3)
    kv: confloat(gt=0)
    yearly: Optional[str]
