"""
Command line utility for EMeRGE
"""

# standard imports
from pathlib import Path
import datetime

# third-party imports
import click

# internal imports
from emerge.metrics.snapshot_metrics import compute_snapshot_metrics
from emerge.metrics import system_metrics
from emerge.metrics import observer
from emerge.metrics import node_metrics
from emerge.simulator import simulation_manager
from emerge.network import feeder_geojson
from emerge.simulator import opendss
from emerge.cli.scenario import generate_scenarios
from emerge.cli.multiscenario_metrics import (
    compute_multiscenario_time_series_metrics,
)
from emerge.cli.custom_metrics import compute_custom_metrics
from emerge.cli.schema_generator import create_schemas


@click.command()
@click.option(
    "-m",
    "--master-file",
    help="Path to master dss file",
)
@click.option(
    "-o",
    "--output-folder",
    default="./geojsons",
    show_default=True,
    help="Ouput directory for storing the geojsons",
)
# @click.option(
#     "-f",
#     "--file-identifier",
#     default="feeder_file_id",
#     show_default=True,
#     help="Input file name (feeder) reference.",    
# )
def create_geojsons(master_file, output_folder): # , feeder_file_id
    """Command line function to generate geojsons from opendss model"""
    
    opendss_instance = opendss.OpenDSSSimulator(master_file)
    # print("handling file id : ", feeder_file_id)
    feeder_geojson.create_feeder_geojson(
        opendss_instance.dss_instance, output_folder # , feeder_file_id
    )


@click.command()
@click.option(
    "-m",
    "--master-file",
    help="Path to master dss file",
)
@click.option(
    "-ss",
    "--simulation-start",
    default="2022-1-1 00:00:00",
    show_default=True,
    help="Simulation start time.",
)
@click.option(
    "-ps",
    "--profile-start",
    default="2022-1-1 00:00:00",
    show_default=True,
    help="Time series profile start time.",
)
@click.option(
    "-se",
    "--simulation-end",
    default="2022-1-2 00:00:00",
    show_default=True,
    help="Simulation end time.",
)
@click.option(
    "-r",
    "--simulation-resolution",
    default=60,
    show_default=True,
    help="Simulation time resolution in minutes.",
)
@click.option(
    "-ot",
    "--overvoltage-threshold",
    default=1.05,
    show_default=True,
    help="Overvoltage threshold.",
)
@click.option(
    "-ut",
    "--undervoltage-threshold",
    default=0.95,
    show_default=True,
    help="Undervoltage threshold.",
)
@click.option(
    "-tt",
    "--thermal-threshold",
    default=0.95,
    show_default=True,
    help="Thermal laoding threshold.",
)
@click.option(
    "-o",
    "--output-json",
    default="db_metric.json",
    show_default=True,
    help="Ouput directory for storing the db",
)
def compute_time_series_metrics(
    master_file,
    simulation_start,
    profile_start,
    simulation_end,
    simulation_resolution,
    overvoltage_threshold,
    undervoltage_threshold,
    thermal_threshold,
    output_json,
):
    """Reads the OpenDSS model and computes various snapshot
    metrics which can be later ingested by dashboard."""

    date_format = "%Y-%m-%d %H:%M:%S"
    manager = simulation_manager.OpenDSSSimulationManager(
        master_file,
        datetime.datetime.strptime(simulation_start, date_format),
        datetime.datetime.strptime(profile_start, date_format),
        datetime.datetime.strptime(simulation_end, date_format),
        simulation_resolution,
    )
    subject = observer.MetricsSubject()

    sardi_voltage_observer = system_metrics.SARDI_voltage(
        overvoltage_threshold, undervoltage_threshold
    )
    sardi_line_observer = system_metrics.SARDI_line(thermal_threshold)
    sardi_xfmr_observer = system_metrics.SARDI_transformer(thermal_threshold)
    sardi_aggregated_observer = system_metrics.SARDI_aggregated(
        loading_limit=thermal_threshold,
        voltage_limit={
            "overvoltage_threshold": overvoltage_threshold,
            "undervoltage_threshold": undervoltage_threshold,
        },
    )
    nvri_observer = node_metrics.NVRI(
        overvoltage_threshold, undervoltage_threshold
    )
    llri_observer = node_metrics.LLRI(thermal_threshold)
    tlri_observer = node_metrics.TLRI(thermal_threshold)

    observers_ = [
        sardi_voltage_observer,
        sardi_line_observer,
        sardi_xfmr_observer,
        sardi_aggregated_observer,
        nvri_observer,
        llri_observer,
        tlri_observer,
    ]
    for observer_ in observers_:
        subject.attach(observer_)

    manager.simulate(subject)
    observer.export_tinydb_json(observers_, output_json)


@click.command()
@click.option(
    "-m",
    "--master-file",
    help="Path to master dss file",
)
@click.option(
    "-o",
    "--output-json",
    default="db.json",
    show_default=True,
    help="Ouput directory for storing the db",
)
def snapshot_metrics(master_file, output_json):
    """Compute snapshot metrics."""
    compute_snapshot_metrics(Path(master_file), output_json)


@click.group()
def cli():
    """Entry point"""

cli.add_command(snapshot_metrics)
cli.add_command(compute_time_series_metrics)
cli.add_command(create_geojsons)
cli.add_command(generate_scenarios)
cli.add_command(compute_multiscenario_time_series_metrics)
cli.add_command(compute_custom_metrics)
cli.add_command(create_schemas)


if __name__ == "__main__":
    create_geojsons()