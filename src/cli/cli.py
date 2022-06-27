"""
Command line utility for EMeRGE
"""

# standard imports 
from pathlib import Path

# third-party imports 
import click

# internal imports
from metrics.compute_snapshot_metrics import compute_snapshot_metrics
from dashboard.snapshot_dashboard import run_server


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
def snapshot_metrics(
    master_file, output_json
):
    """Reads the OpenDSS model and computes various snapshot metrics which can be later ingested by dashboard """
    compute_snapshot_metrics(
        Path(master_file),
        output_json
    )


@click.command()
@click.option(
    "-db",
    "--db-json",
    help="Path to DB JSON file",
)
@click.option(
    "-d",
    "--debug",
    default=False,
    show_default=True,
    help="Turn this on if you want debug to be true!",
)

@click.option(
    "-p",
    "--port",
    default=8050,
    show_default=True,
    help="Port where you want the server to run!",
)
def serve(
    db_json,  debug, port
):
    """ Takes the db json and creates EMERGE dashboard """
    run_server(
      db_json, debug, port
    )



@click.group()
def cli():
    """Entry point"""

cli.add_command(snapshot_metrics)
cli.add_command(serve)