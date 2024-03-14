"""
Command line utility for EMeRGE
"""

from pathlib import Path

import click

from emerge.metrics.snapshot_metrics import compute_snapshot_metrics
from emerge.network import feeder_geojson
from emerge.simulator import opendss
from emerge.cli.scenario import generate_scenarios
from emerge.cli.multiscenario_metrics import (
    multi_timeseries_simulation,
)
from emerge.cli.custom_metrics import compute_custom_metrics
from emerge.cli.schema_generator import create_schemas
from emerge.cli.timeseries_simulation import timeseries_simulation
from emerge.cli.nodal_hosting_capacity import nodal_hosting_analysis


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
def create_geojsons(master_file, output_folder):
    """Command line function to generate geojsons from opendss model"""
    
    opendss_instance = opendss.OpenDSSSimulator(master_file)
    feeder_geojson.create_feeder_geojson(
        opendss_instance.dss_instance, output_folder
    )

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
cli.add_command(timeseries_simulation)
cli.add_command(create_geojsons)
cli.add_command(generate_scenarios)
cli.add_command(multi_timeseries_simulation)
cli.add_command(compute_custom_metrics)
cli.add_command(create_schemas)
cli.add_command(nodal_hosting_analysis)