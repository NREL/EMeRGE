""" This module contains function for exposing scenarios generation as CLI."""

import click
import json

from emerge.scenarios import (
    data_model,
    scenario,
    opendss_writer,
)
from emerge.utils import dss_util
from emerge.simulator import opendss


@click.command()
@click.option(
    "-c",
    "--config",
    help="Path to config file for generating scenarios",
)
def generate_scenarios(config):
    """Function to create PV deloyment scenarios."""
    # pylint: disable=no-member
    with open(config, "r", encoding="utf-8") as file:
        config_dict = json.load(file)

    config_data = data_model.DERScenarioConfigModel.model_validate(config_dict)

    for der_scen in config_data.der_scenario:
        simulator = opendss.OpenDSSSimulator(config_data.master_file)
        list_of_customers = dss_util.get_list_of_customer_models(
            simulator.dss_instance, 1, cust_type=config_data.opendss_attr
        )
        mapper_object = dss_util.get_load_mapper_objects(simulator.dss_instance)

        derscenarios = scenario.create_der_scenarios(
            list_of_customers,
            data_model.ScenarioBaseConfig(
                **config_data.model_dump(
                    include=["pct_resolution", "num_of_penetration", "max_num_of_samples"]
                )
            ),
            der_config=der_scen,
        )
        writer_object = opendss_writer.OpenDSSPVScenarioWriter(
            derscenarios, config_data.output_folder
        )
        writer_object.write(mapper_object, file_name=der_scen.file_name)
