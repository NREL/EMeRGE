
from typing import Optional
from pathlib import Path

from sqlmodel import Field, SQLModel, create_engine


class HostingCapacityResult(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    hoting_capacity_kw: float


def create_table(sqlite_file: Path):
    """ Function to create sqlite table."""

    engine = create_engine(f"sqlite:///{str(sqlite_file)}")
    SQLModel.metadata.create_all(engine)
    return engine