""" This module contains function that would compute nodal hosting 
capacity.

Idea is to loop through all the nodes. Increase the solar capacity by step kw specified
by user and return max capacity for which the risk would be zero.
"""
from pathlib import Path
from typing import Annotated
from datetime import datetime
import json
import multiprocessing

import click
from emerge.metrics.system_metrics import SARDI_aggregated
from emerge.simulator.simulation_manager import OpenDSSSimulationManager
import numpy as np
import polars as pl
from pydantic import BaseModel, Field
from loguru import logger
from sqlmodel import Session

from emerge.cli import get_num_core
from emerge.metrics import observer
from emerge.simulator import opendss
from emerge.cli.create_sqlite_table import create_table, HostingCapacityResult

class BasicSimulationSettings(BaseModel):
    """Interface for basic simulation settings."""
    
    master_dss_file: Annotated[Path, Field(..., description="Path to master dss file.")]
    start_time: Annotated[datetime, Field(..., description="Start time for simulation.")]
    end_time: Annotated[datetime, Field(..., description="End time for simulation.")]
    profile_start_time: Annotated[datetime, Field(..., description="Profile start time.")]
    resolution_min: Annotated[float, Field(60, gt=0, description="Simulation time resolution in minute.")]
    

class SingleNodeHostingCapacityInput(BasicSimulationSettings):
    """Interface for single node hosting capacity."""
    step_kw: Annotated[float, Field(gt=0, description="kW value to increase pv capacity by each time.")]
    max_kw: Annotated[float, Field(gt=0, description="Maximum kw to not exceed.")]
    

class MultiNodeHostingCapacityInput(SingleNodeHostingCapacityInput):
    """Interface for timeseries simulation input model."""

    num_core: Annotated[int, Field(ge=1, description="Number of cores to use for parallel simulation.")]
    export_sqlite_path: Annotated[Path, Field(..., description="Sqlite file to export nodal hosting capacity.")]
    pv_profile: Annotated[str, Field(..., description="Name of the profile for pv system")]

def _compute_hosting_capacity(input):
    """ Wrapper around compute hosting capacity. """
    return compute_hosting_capacity(*input)

def compute_hosting_capacity(config: SingleNodeHostingCapacityInput, bus: str, pv_profile: str) -> tuple[float, str]:
    """ Function to compute node hosting capacity."""
    hosting_capacity = 0
    opendss_instance = opendss.OpenDSSSimulator(config.master_dss_file)
    opendss_instance.dss_instance.Circuit.SetActiveBus(bus)
    bus_kv = opendss_instance.dss_instance.Bus.kVBase()
    pv_name = f"{bus}_pv"

    new_pv = f"new PVSystem.{pv_name} bus1={bus} "
    f"kv={round(bus_kv,2 )} phases=3 kVA=1000 Pmpp=1000 "
    f"PF=1.0 yearly={pv_profile}"

    opendss_instance.dss_instance.run_command(new_pv)
    
    for capacity in np.arange(config.step_kw, config.max_kw, config.step_kw):
        opendss_instance.dss_instance.run_command(
            f"pvsystem.{pv_name}.kva={capacity}")
        opendss_instance.dss_instance.run_command(
            f"pvsystem.{pv_name}.pmpp={capacity}")
        
        sim_manager = OpenDSSSimulationManager(
            opendss_instance=opendss_instance,
            simulation_start_time=config.start_time,
            profile_start_time=config.profile_start_time,
            simulation_end_time=config.end_time,
            simulation_timestep_min=config.resolution_min
        )

        subject = observer.MetricsSubject()
        sardi_observer = SARDI_aggregated()
        subject.attach(sardi_observer)

        sim_manager.simulate(subject=subject)
        logger.info(f"Bus finished {bus}, capacity {capacity}")
        sardi_aggregated = pl.from_dict(
                    sardi_observer.get_metric()
                )['sardi_aggregated'].to_list()[0]
        
        if sardi_aggregated > 0:
            break
        hosting_capacity = capacity

    return hosting_capacity, bus


@click.command()
@click.option(
    "-c",
    "--config",
    help="Path to config file for running timeseries simulation",
)
def nodal_hosting_analysis(
   config: str
):
    """Run multiscenario time series simulation and compute
    time series metrics."""

    with open(config, "r", encoding="utf-8") as file:
        config_dict = json.load(file)

    config: MultiNodeHostingCapacityInput = MultiNodeHostingCapacityInput.model_validate(config_dict)

    opendss_instance = opendss.OpenDSSSimulator(config.master_dss_file)
    buses = opendss_instance.dss_instance.Circuit.AllBusNames()

    engine = create_table(config.export_sqlite_path)

    num_core = get_num_core.get_num_core(config.num_core, len(buses))
    with multiprocessing.Pool(int(num_core)) as pool:
        data_to_process = [
            [SingleNodeHostingCapacityInput.model_validate(config.model_dump()),
             bus,
             config.pv_profile] for bus in buses
        ]
        async_results = [pool.apply_async(_compute_hosting_capacity, (data,)) for data in data_to_process]
        
        with Session(engine) as session:
            for result in async_results:
                capacity, bus_ = result.get()
                session.add(HostingCapacityResult(name=bus_, hoting_capacity_kw=capacity))
                session.commit()