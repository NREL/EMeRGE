"""This module implements cli function to 
run powerflow on single opendss model."""

from datetime import datetime
from pathlib import Path
from typing import Annotated
from emerge.cli import get_observers
from emerge.cli.get_observers import SimulationMetrics
from emerge.metrics import observer
from emerge.simulator.simulation_manager import OpenDSSSimulationManager

from pydantic import BaseModel, Field


class SingleModelSimulationInput(BaseModel):
    """Class interface for single model simulation input."""

    master_dss_file: Annotated[Path, Field(..., description="Path to master dss file.")]
    start_time: Annotated[datetime, Field(..., description="Start time for simulation.")]
    end_time: Annotated[datetime, Field(..., description="End time for simulation.")]
    profile_start_time: Annotated[datetime, Field(..., description="Profile start time.")]
    export_path: Annotated[Path, Field(..., description="Path to export metric results.")]
    resolution_min: Annotated[float, Field(60, gt=0, description="Simulation time resolution in minute.")]
    metrics: Annotated[SimulationMetrics, Field(SimulationMetrics(), description="Simulation metrics.")]

def compute_single_model_timeseries_metrics(config: SingleModelSimulationInput):
    """ Function to compute single model timeseries metrics."""

    manager = OpenDSSSimulationManager(
        path_to_master_dss_file=config.master_dss_file,
        simulation_start_time=config.start_time,
        profile_start_time=config.profile_start_time,
        simulation_end_time=config.end_time,
        simulation_timestep_min=config.resolution_min
    )
    subject = observer.MetricsSubject()
    observers = get_observers.get_observers(config.metrics.model_dump())

    for _, observer_ in observers.items():
        subject.attach(observer_)

    manager.simulate(subject)
    manager.export_convergence(config.export_path / 'convergence_report.csv')
    observer.export_csv(list(observers.values()), config.export_path)


if __name__ == "__main__":
    config = SingleModelSimulationInput(
        start_time=datetime(2023,1,1,0,0,0),
        end_time=datetime(2023,1,1,23,0,0),
        profile_start_time=datetime(2023,1,1,0,0,0),
        export_path="/home/ec2-user/panynj/exports/feb_9_test",
        master_dss_file="/home/ec2-user/panynj/opendss_models/lga_east_end_substation/new_master.dss"
    )
    compute_single_model_timeseries_metrics(
        config
    )