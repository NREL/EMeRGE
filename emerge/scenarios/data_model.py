""" Module for handling data model used in scenario generation. """


from typing import List

from pydantic import BaseModel, confloat, conint, Field


class CustomerModel(BaseModel):
    name: str
    kw: float
    distance: float


class PVScenarioConfig(BaseModel):
    pct_resolution: confloat(gt=0, le=100) = Field(
        description="Percentage resolution or step resolution"
    )
    num_of_penetration: conint(gt=0)
    max_num_of_samples: conint(ge=1) = 1
    capacity_factor: confloat(gt=0, le=1) = 0.3
    load_factor: confloat(gt=0, le=1) = 0.33
    max_pct_production: confloat(gt=0, le=500) = 100


class PVModel(BaseModel):
    name: str
    kw: confloat(ge=0)
    customer: str


class DistPVScenarioModel(BaseModel):
    name: str
    sample_id: int
    pv_penetration: float
    pvs: List[PVModel]


class LoadMetadataModel(BaseModel):
    name: str
    bus: str
    num_phase: conint(ge=1, le=3)
    kv: confloat(gt=0)
