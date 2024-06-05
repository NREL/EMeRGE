""" Module for handling data model used in scenario generation. """


from typing import List, Optional, Dict
from enum import Enum

from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError
from typing_extensions import Annotated, Literal


class CustomerModel(BaseModel):
    """Interface for representing customer used in pv scenario development."""

    name: str
    kw: float
    distance: float
    cust_type: Optional[str] = None


class DERType(str, Enum):
    """Available der enum types."""

    # pylint: disable=invalid-name
    load = "load"
    solar = "solar"


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

    capacity_factor: Annotated[float, Field(gt=0, le=1)] = 0.3
    load_factor: Annotated[float, Field(gt=0, le=1)] = 0.33
    max_pct_production: Annotated[float, Field(gt=0, le=500)] = 100
    profile: str


class SizeWithProbabilityModel(BaseModel):
    """Use this model if you want to pick sizes with probabilities."""

    sizes: List[float] | float
    probabilites: List[Annotated[float, Field(ge=0, le=1)]] | float
    profile: List[str] | str

    @model_validator(mode="after")
    def validate_lengths_are_same(self) -> "SizeWithProbabilityModel":
        if (
            isinstance(self.sizes, list)
            or isinstance(self.probabilites, list)
            or isinstance(self.profile, list)
        ):
            try:
                if len(self.sizes) == len(self.probabilites) == len(self.profile):
                    return self
                raise ValueError("Length must match for sizes,  probabilities and profile names. ")
            except Exception as error:
                raise PydanticCustomError("mixed_type", f"Error validating fields : {error}")
        return self


class _DERScenarioInput(BaseModel):
    """Base input model for der scenarios."""

    sizing_strategy: CapacityStrategyEnum
    der_type: DERType
    der_tag: str = ""
    energy_sizing_input: Dict[
        str, EnergyBasedSolarSizingStrategyInput
    ] | EnergyBasedSolarSizingStrategyInput | None = None
    peakmult_sizing_input: Dict[
        str, SizeWithProbabilityModel
    ] | SizeWithProbabilityModel | None = None
    fixed_sizing_input: Dict[
        str, SizeWithProbabilityModel
    ] | SizeWithProbabilityModel | None = None


class DERScenarioInput(_DERScenarioInput):
    """Input model for der scenarios."""

    selection_strategy: SelectionStrategyEnum
    other_ders: List[_DERScenarioInput]


class BasicDERModel(BaseModel):
    """Basic DER model used in solar scenario development."""

    name: str
    kw: Annotated[float, Field(ge=0)]
    customer: CustomerModel
    der_type: DERType
    der_tag: str = ""
    profile: str


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
    num_phase: Annotated[int, Field(ge=1, le=3)]
    kv: Annotated[float, Field(gt=0)]
    yearly: Optional[str] = None


class DERScenarioInputModel(_DERScenarioInput):
    """Interface for der scenario input model."""

    file_name: str
    selection_strategy: SelectionStrategyEnum
    other_ders: List[_DERScenarioInput]


class ScenarioBaseConfig(BaseModel):
    """Interface for basic settings in defining scenario."""

    pct_resolution: Annotated[float, Field(gt=0, le=100)] = Field(
        description="Percentage resolution or step resolution"
    )
    num_of_penetration: Annotated[int, Field(gt=0)]
    max_num_of_samples: Annotated[int, Field(ge=1)] = 1


class DERScenarioConfigModel(ScenarioBaseConfig):
    """CLI interface model for generating solar scenarios."""

    master_file: str
    output_folder: str
    opendss_attr: Literal["yearly", "class"] = "class"
    der_scenario: List[DERScenarioInputModel]
