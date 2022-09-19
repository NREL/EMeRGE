""" This module contains function for exposing scenarios generation as CLI."""

import click

from emerge.scenarios import data_model, pv_scenario, strategy, opendss_writer
from emerge.utils import dss_util
from emerge.simulator import opendss


@click.command()
@click.option(
    "-m",
    "--master-file",
    help="Path to master dss file",
)
@click.option(
    "-o",
    "--output-folder",
    default="./scenarios",
    show_default=True,
    help="Ouput directory for storing the scenarios",
)
@click.option(
    "-ppr",
    "--pct-penetration-resolution",
    default=10,
    show_default=True,
    help="Percentage penetration resolution",
)
@click.option(
    "-np",
    "--number-of-penetrations",
    default=10,
    show_default=True,
    help="Number of penetrations",
)
@click.option(
    "-ms",
    "--maximum-samples",
    default=1,
    show_default=True,
    help="Maximum number of samples",
)
@click.option(
    "-pae",
    "--percentage-annual-energy",
    default=100,
    show_default=True,
    help="Percentage annual energy consumption expected to be supplied by pv",
)
@click.option(
    "-lf",
    "--load-factor",
    default=0.33,
    show_default=True,
    help="Annual load factor",
)
@click.option(
    "-cf",
    "--capacity-factor",
    default=0.33,
    show_default=True,
    help="Annual solar capacity factor",
)
@click.option(
    "-s",
    "--strategy-name",
    type=click.Choice(["random", "far", "close"]),
    default="random",
    show_default=True,
    help="Selection strategy",
)
@click.option(
    "-lm",
    "--load-multiplier",
    default=1.0,
    show_default=True,
    help="Multiplier to be used to reduce load",
)
def generate_pv_scenarios_for_feeder(
    master_file,
    output_folder,
    pct_penetration_resolution,
    number_of_penetrations,
    maximum_samples,
    percentage_annual_energy,
    load_factor,
    capacity_factor,
    strategy_name,
    load_multiplier
):
    """Function to create PV deloyment scenarios."""

    config = data_model.PVScenarioConfig(
        pct_resolution=pct_penetration_resolution,
        num_of_penetration=number_of_penetrations,
        max_num_of_samples=maximum_samples,
        capacity_factor=capacity_factor,
        load_factor=load_factor,
        max_pct_production=percentage_annual_energy,
    )

    strategy_ = {
        "random": strategy.RandomSelectionStrategy(),
        "far": strategy.FarSelectionStrategy(),
        "close": strategy.CloseSelectionStrategy(),
    }[strategy_name]

    simulator = opendss.OpenDSSSimulator(master_file)
    list_of_customers = dss_util.get_list_of_customer_models(
        simulator.dss_instance, load_multiplier
    )
    mapper_object = dss_util.get_load_mapper_objects(simulator.dss_instance)

    scenario_instance = pv_scenario.DistributedPVScenario(
        list_of_customers, config
    )
    pvscenarios = scenario_instance.create_pv_scenarios_for_feeder(strategy_)
    writer_object = opendss_writer.OpenDSSPVScenarioWriter(
        pvscenarios, output_folder
    )
    writer_object.write(mapper_object)
