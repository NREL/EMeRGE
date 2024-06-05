"""This module implements cli function to
run powerflow on single opendss model."""

from datetime import datetime
from pathlib import Path
from typing import Annotated
import json
from emerge.simulator.opendss import OpenDSSSimulator

from pydantic import BaseModel, Field
import click

from emerge.cli import get_observers
from emerge.cli.get_observers import SimulationMetrics
from emerge.metrics import observer
from emerge.simulator.simulation_manager import OpenDSSSimulationManager


class TimeseriesSimulationInput(BaseModel):
    """Interface for timeseries simulation input model."""

    master_dss_file: Annotated[Path, Field(..., description="Path to master dss file.")]
    start_time: Annotated[datetime, Field(..., description="Start time for simulation.")]
    end_time: Annotated[datetime, Field(..., description="End time for simulation.")]
    profile_start_time: Annotated[datetime, Field(..., description="Profile start time.")]
    export_path: Annotated[Path, Field(..., description="Path to export metric results.")]
    resolution_min: Annotated[
        float, Field(60, gt=0, description="Simulation time resolution in minute.")
    ]
    metrics: Annotated[
        SimulationMetrics, Field(SimulationMetrics(), description="Simulation metrics.")
    ]


def compute_timeseries_simulation_metrics(config: TimeseriesSimulationInput):
    """Function to compute metrics for timeseries simulation."""

    opendss_instance = OpenDSSSimulator(config.master_dss_file)

    manager = OpenDSSSimulationManager(
        opendss_instance=opendss_instance,
        simulation_start_time=config.start_time,
        profile_start_time=config.profile_start_time,
        simulation_end_time=config.end_time,
        simulation_timestep_min=config.resolution_min,
    )
    subject = observer.MetricsSubject()
    observers = get_observers.get_observers(config.metrics.model_dump())

    for _, observer_ in observers.items():
        subject.attach(observer_)

    manager.simulate(subject)
    manager.export_convergence(config.export_path / "convergence_report.csv")
    observer.export_csv(list(observers.values()), config.export_path)


@click.command()
@click.option(
    "-c",
    "--config",
    help="Path to config file for generating scenarios",
)
def timeseries_simulation(config):
    """Function to run timeseries simulation."""

    with open(config, "r", encoding="utf-8") as file:
        config_dict = json.load(file)

    config = TimeseriesSimulationInput.model_validate(config_dict)
    compute_timeseries_simulation_metrics(config)
