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
import time
import math

import click
import numpy as np
import polars as pl
from pydantic import BaseModel, Field
from loguru import logger
from sqlmodel import Session

from emerge.cli import get_num_core
from emerge.metrics import observer
from emerge.simulator import opendss
from emerge.cli.nodal_hosting_sqlite_tables import (
    HostingCapacityReport,
    OverloadedLinesReport,
    SimulationConvergenceReport,
    SimulationTime,
    TotalEnergyReport,
    create_table,
    get_engine,
)
from emerge.metrics.line_loading_stats import OverloadedLines
from emerge.metrics.system_metrics import (
    SARDI_aggregated,
    SARDI_line,
    SARDI_voltage,
    TotalEnergy,
    TotalPVGeneration,
)
from emerge.simulator.simulation_manager import OpenDSSSimulationManager


class BasicSimulationSettings(BaseModel):
    """Interface for basic simulation settings."""

    master_dss_file: Annotated[Path, Field(..., description="Path to master dss file.")]
    start_time: Annotated[datetime, Field(..., description="Start time for simulation.")]
    end_time: Annotated[datetime, Field(..., description="End time for simulation.")]
    profile_start_time: Annotated[datetime, Field(..., description="Profile start time.")]
    resolution_min: Annotated[
        float, Field(60, gt=0, description="Simulation time resolution in minute.")
    ]


class SingleNodeHostingCapacityInput(BasicSimulationSettings):
    """Interface for single node hosting capacity."""

    step_kw: Annotated[
        float, Field(gt=0, description="kW value to increase pv capacity by each time.")
    ]
    max_kw: Annotated[float, Field(gt=0, description="Maximum kw to not exceed.")]


class MultiNodeHostingCapacityInput(SingleNodeHostingCapacityInput):
    """Interface for timeseries simulation input model."""

    num_core: Annotated[
        int, Field(ge=1, description="Number of cores to use for parallel simulation.")
    ]
    export_sqlite_path: Annotated[
        Path, Field(..., description="Sqlite file to export nodal hosting capacity.")
    ]
    pv_profile: Annotated[str, Field(..., description="Name of the profile for pv system")]


class NodalHostingCapacityReport:
    """Class interface for capturing nodal hosting capacity results."""

    def __init__(self):
        self.subject = observer.MetricsSubject()
        self.sardi_agg = SARDI_aggregated()
        self.sardi_voltage = SARDI_voltage()
        self.sardi_line = SARDI_line()
        self.solar_generation = TotalPVGeneration()
        self.ol_lines = OverloadedLines()
        self.circuit_energy = TotalEnergy()
        self.export_energy = TotalEnergy(export_only=True)

        for obs in [
            self.sardi_agg,
            self.sardi_voltage,
            self.sardi_line,
            self.solar_generation,
            self.ol_lines,
            self.circuit_energy,
            self.export_energy,
        ]:
            self.subject.attach(obs)

    def is_hosting_capacity_reached(self) -> bool:
        """Method to check if hosting capacity is reached."""
        return self.get_sardi_aggregated() > 0 or self.get_total_export_energy() != 0

    def get_subject(self) -> observer.MetricsSubject:
        """Return subject container containing observers."""
        return self.subject

    def get_overloaded_line_loadings(self) -> dict[str, list[float]]:
        """Returns overloaded lines."""
        return self.ol_lines.get_metric()

    def get_sardi_voltage(self):
        """Returns SARDI voltage metrics."""
        return pl.from_dict(self.sardi_voltage.get_metric())["sardi_voltage"].to_list()[0]

    def get_sardi_aggregated(self):
        """Method to return SARDI aggregate metric."""
        return pl.from_dict(self.sardi_agg.get_metric())["sardi_aggregated"].to_list()[0]

    def get_sardi_line(self):
        """Method to return SARDI line metric."""
        return pl.from_dict(self.sardi_line.get_metric())["sardi_line"].to_list()[0]

    def get_solar_total_energy(self):
        """Method to return total solar energy."""
        return pl.from_dict(self.solar_generation.get_metric())["active_power"].to_list()[0]

    def get_circuit_total_energy(self):
        """Method to get circuit total energy."""
        return pl.from_dict(self.circuit_energy.get_metric())["active_power"].to_list()[0]

    def get_total_export_energy(self):
        """Method to get total export energy."""
        return pl.from_dict(self.export_energy.get_metric())["active_power"].to_list()[0]


def _compute_hosting_capacity(input):
    """Wrapper around compute hosting capacity."""
    return compute_hosting_capacity(*input)


def compute_hosting_capacity(
    config: SingleNodeHostingCapacityInput, bus: str, pv_profile: str, sqlite_file: Path
):
    """Function to compute node hosting capacity."""
    hosting_capacity = 0
    engine = get_engine(sqlite_file)

    for capacity in np.arange(config.step_kw, config.max_kw, config.step_kw):
        opendss_instance = opendss.OpenDSSSimulator(config.master_dss_file)
        opendss_instance.dss_instance.Circuit.SetActiveBus(bus)
        bus_kv = round(opendss_instance.dss_instance.Bus.kVBase() * math.sqrt(3), 2)
        pv_name = f"{bus}_pv"

        new_pv = (
            f"new PVSystem.{pv_name} bus1={bus} kv={round(bus_kv,2 )} "
            + f"phases=3 kVA={capacity} Pmpp={capacity} PF=1.0 yearly={pv_profile}"
        )
        logger.info(new_pv)

        opendss_instance.dss_instance.run_command(new_pv)
        opendss_instance.recalc()
        opendss_instance.solve()

        sim_manager = OpenDSSSimulationManager(
            opendss_instance=opendss_instance,
            simulation_start_time=config.start_time,
            profile_start_time=config.profile_start_time,
            simulation_end_time=config.end_time,
            simulation_timestep_min=config.resolution_min,
        )

        report_instance = NodalHostingCapacityReport()
        logger.info(f"Node started {bus}, capacity {capacity}")

        start_time = time.time()
        sim_manager.simulate(subject=report_instance.get_subject())
        end_time = time.time()
        logger.info(f"Node finished {bus}, " f"elpased time {end_time - start_time} seconds")

        with Session(engine) as session:
            for timestamp, conv_ in zip(
                sim_manager.convergence_dict["datetime"],
                sim_manager.convergence_dict["convergence"],
            ):
                session.add(
                    SimulationConvergenceReport(
                        node_name=bus, convergence=conv_, capacity_kw=capacity, timestamp=timestamp
                    )
                )

            session.add(
                SimulationTime(
                    node_name=bus, capacity=capacity, compute_sec=(end_time - start_time)
                )
            )

            session.add(
                TotalEnergyReport(
                    node_name=bus,
                    pv_capacity_kw=capacity,
                    pv_energy_mwh=report_instance.get_solar_total_energy(),
                    circuit_energy_mwh=report_instance.get_circuit_total_energy(),
                )
            )

            for ol_line, loadings in report_instance.get_overloaded_line_loadings().items():
                session.add(
                    OverloadedLinesReport(
                        start_time=config.start_time,
                        resolution_min=config.resolution_min,
                        node_name=bus,
                        line_name=ol_line,
                        loadings=str(loadings),
                    )
                )

            session.commit()

        if report_instance.is_hosting_capacity_reached() > 0:
            break

        hosting_capacity = capacity

    with Session(engine) as session:
        session.add(
            HostingCapacityReport(
                node_name=bus,
                hosting_capacity_kw=hosting_capacity,
                sardi_voltage=report_instance.get_sardi_voltage(),
                sardi_aggregated=report_instance.get_sardi_aggregated(),
                sardi_line=report_instance.get_sardi_line(),
            )
        )
        session.commit()


@click.command()
@click.option(
    "-c",
    "--config",
    help="Path to config file for running timeseries simulation",
)
@click.option(
    "-n",
    "--nodes",
    default="",
    show_default=True,
    help="List of comma separated nodes",
)
def nodal_hosting_analysis(config: str, nodes: str):
    """Run multiscenario time series simulation and compute
    time series metrics."""

    analysis_start_time = time.time()
    with open(config, "r", encoding="utf-8") as file:
        config_dict = json.load(file)

    config: MultiNodeHostingCapacityInput = MultiNodeHostingCapacityInput.model_validate(
        config_dict
    )

    if not nodes:
        opendss_instance = opendss.OpenDSSSimulator(config.master_dss_file)
        buses = opendss_instance.dss_instance.Circuit.AllBusNames()
    else:
        buses = nodes.split(",")

    create_table(config.export_sqlite_path)
    num_core = get_num_core.get_num_core(config.num_core, len(buses))
    with multiprocessing.Pool(int(num_core)) as pool:
        data_to_process = [
            [
                SingleNodeHostingCapacityInput.model_validate(config.model_dump()),
                bus,
                config.pv_profile,
                config.export_sqlite_path,
            ]
            for bus in buses
        ]
        pool.map(_compute_hosting_capacity, data_to_process)
    analysis_end_time = time.time()
    print(f"Required time: {analysis_end_time - analysis_start_time} seconds, num_core={num_core}")
