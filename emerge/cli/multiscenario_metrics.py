""" Module for computing time series metrics for multi scenario simulation."""
from pathlib import Path
import multiprocessing
from typing import Annotated
import json

import click
from emerge.cli import get_num_core, get_observers
from emerge.cli.timeseries_simulation import TimeseriesSimulationInput

from emerge.metrics import observer
from emerge.simulator import simulation_manager
from emerge.simulator.opendss import OpenDSSSimulator
from pydantic import Field


class ScenarioTimeseriesSimulationInput(TimeseriesSimulationInput):
    scenario_file: Annotated[Path, Field(..., description="Path to .dss file to load")]


def _run_timeseries_sim(config: ScenarioTimeseriesSimulationInput):
    opendss_instance = OpenDSSSimulator(config.master_dss_file)
    opendss_instance.post_redirect(config.scenario_file.absolute())

    manager = simulation_manager.OpenDSSSimulationManager(
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

    export_folder = Path(config.export_path) / config.scenario_file.stem
    export_folder.mkdir(exist_ok=True, parents=True)
    manager.export_convergence(export_folder / "convergence_report.csv")
    observer.export_csv(list(observers.values()), export_folder)


@click.command()
@click.option(
    "-c",
    "--config",
    help="Path to config file for generating scenarios",
)
@click.option(
    "-sf",
    "--scenario_folder",
    help="Path to scenario folder",
)
@click.option(
    "-nc",
    "--num-core",
    default=1,
    show_default=True,
    help="Num of cores to run simulation with.",
)
def multi_timeseries_simulation(config: str, scenario_folder: str, num_core: int):
    """Run multiscenario time series simulation and compute
    time series metrics."""
    with open(config, "r", encoding="utf-8") as file:
        config_dict = json.load(file)

    config = TimeseriesSimulationInput.model_validate(config_dict)

    scenario_folder = Path(scenario_folder)
    timeseries_input = []
    for file_path in scenario_folder.iterdir():
        if file_path.suffix == ".dss":
            timeseries_input.append(
                ScenarioTimeseriesSimulationInput(**config.model_dump(), scenario_file=file_path)
            )

    num_core = get_num_core(num_core, len(timeseries_input))

    if num_core > 0:
        with multiprocessing.Pool(int(num_core)) as p:
            p.map(_run_timeseries_sim, timeseries_input)
