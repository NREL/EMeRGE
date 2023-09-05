""" This module contains function for exposing scenarios generation as CLI."""

import click
import json

import pydantic

from emerge.scenarios import (
    data_model,
    scenario,
    sizing_strategy,
    selection_strategy,
    opendss_writer,
)
from emerge.utils import dss_util
from emerge.simulator import opendss
from emerge.cli.interface import PVSceanarioCliInputModel


@click.command()
@click.option(
    "-c",
    "--config",
    help="Path to config file for generating scenarios",
)
@click.option(
    "-ct",
    "--customer-type",
    default="class",
    show_default=True,
    help="OpenDSS attribute used for extracting customer type.",
)
def generate_pv_scenarios_for_feeder(config, customer_type):
    """Function to create PV deloyment scenarios."""
    # pylint: disable=no-member
    with open(config, "r", encoding="utf-8") as file:
        config_dict = json.load(file)
    config_data = pydantic.parse_obj_as(
        PVSceanarioCliInputModel, config_dict)
    
    for der_scen in config_data.der_scenario:

        simulator = opendss.OpenDSSSimulator(config_data.master_file)
        list_of_customers = dss_util.get_list_of_customer_models(simulator.dss_instance, 1, cust_type=customer_type)
        mapper_object = dss_util.get_load_mapper_objects(simulator.dss_instance)

        derscenarios = scenario.create_der_scenarios(
            list_of_customers, config_data.basic_config,
            der_config=der_scen
        )
        writer_object = opendss_writer.OpenDSSPVScenarioWriter(
            derscenarios, config_data.output_folder
        )
        writer_object.write(mapper_object,
            file_name=der_scen.file_name, tag_name=der_scen.tag_name            
        )
