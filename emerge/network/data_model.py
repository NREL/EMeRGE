"""
 Extract base level metrics
"""

from typing_extensions import Annotated

from pydantic import Field, BaseModel


class LoadAssetMetrics(BaseModel):
    total_count: Annotated[int, Field(ge=0)] = 0
    max_kw_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    min_kw_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    min_kvar_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    max_kvar_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    total_kw_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    total_kvar_capacity: Annotated[float, Field(ge=0.0)] = 0.0


class PVAssetMetrics(BaseModel):
    total_count: Annotated[int, Field(ge=0)] = 0
    max_kw_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    min_kw_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    total_kw_capacity: Annotated[float, Field(ge=0.0)] = 0.0


class CapacitorAssetMetrics(BaseModel):
    total_count: Annotated[int, Field(ge=0)] = 0
    max_kvar_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    min_kvar_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    total_kvar_capacity: Annotated[float, Field(ge=0.0)] = 0.0


class RegulatorsAssetMetrics(BaseModel):
    total_count: Annotated[int, Field(ge=0)] = 0


class TransformersAssetMetrics(BaseModel):
    total_count: Annotated[int, Field(ge=0)] = 0
    max_kva_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    min_kva_capacity: Annotated[float, Field(ge=0.0)] = 0.0
    total_kva_capacity: Annotated[float, Field(ge=0.0)] = 0.0


class FeederMetrics(BaseModel):
    total_feeder_length_km: Annotated[float, Field(ge=0.0)] = 0.0
    max_primary_feeder_length_km: Annotated[float, Field(ge=0.0)] = 0.0
    max_secondary_feeder_length_km: Annotated[float, Field(ge=0.0)] = 0.0
    min_secondary_feeder_length_km: Annotated[float, Field(ge=0.0)] = 0.0
    primary_kv_level: Annotated[float, Field(ge=0.0)] = 0.0
    secondary_kv_level: Annotated[float, Field(ge=0.0)] = 0.0
    total_buses: Annotated[int, Field(ge=0)] = 0
    total_line_sections: Annotated[int, Field(ge=0)] = 0


class AssetMetrics(BaseModel):
    loads: LoadAssetMetrics
    pvs: PVAssetMetrics
    capacitors: CapacitorAssetMetrics
    regulators: RegulatorsAssetMetrics
    transformers: TransformersAssetMetrics
    lines: FeederMetrics
