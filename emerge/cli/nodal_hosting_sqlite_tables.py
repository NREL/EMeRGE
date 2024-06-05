from typing import Optional
from pathlib import Path
from datetime import datetime

from sqlmodel import Field, SQLModel, create_engine


class HostingCapacityReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    node_name: str
    hosting_capacity_kw: float
    sardi_voltage: float
    sardi_line: float
    sardi_aggregated: float


class SimulationTime(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    node_name: str
    capacity: float
    compute_sec: float


class SimulationConvergenceReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    capacity_kw: float
    node_name: str
    convergence: bool
    timestamp: datetime


class TotalEnergyReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    node_name: str
    pv_capacity_kw: float
    pv_energy_mwh: float
    circuit_energy_mwh: float


class OverloadedLinesReport(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    start_time: datetime
    resolution_min: int
    node_name: str
    line_name: str
    loadings: str


def get_engine(sqlite_file: Path):
    return create_engine(f"sqlite:///{str(sqlite_file)}")


def create_table(sqlite_file: Path):
    """Function to create sqlite table."""

    engine = create_engine(f"sqlite:///{str(sqlite_file)}")
    SQLModel.metadata.create_all(engine)
    return engine
