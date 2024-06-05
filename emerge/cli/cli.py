"""Command line utility for EMeRGE."""


import click

from emerge.network import feeder_geojson
from emerge.simulator import opendss
from emerge.cli.scenario import generate_scenarios
from emerge.cli.multiscenario_metrics import (
    multi_timeseries_simulation,
)
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
    feeder_geojson.create_feeder_geojson(opendss_instance.dss_instance, output_folder)


@click.group()
def cli():
    """Entry point"""


cli.add_command(timeseries_simulation)
cli.add_command(create_geojsons)
cli.add_command(generate_scenarios)
cli.add_command(multi_timeseries_simulation)
cli.add_command(create_schemas)
cli.add_command(nodal_hosting_analysis)
