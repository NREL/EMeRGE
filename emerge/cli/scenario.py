""" This module contains function for exposing scenarios generation as CLI."""

import click
import yaml

import pydantic

from emerge.scenarios import (
    data_model,
    pv_scenario,
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
def generate_pv_scenarios_for_feeder(config):
    """Function to create PV deloyment scenarios."""
    # pylint: disable=no-member
    with open(config, "r", encoding="utf-8") as file:
        config_dict = yaml.safe_load(file)
    config_data = pydantic.parse_obj_as(
        PVSceanarioCliInputModel, config_dict)

    select_strategy_ = {
        data_model.SelectionStrategyEnum.random_allocation: selection_strategy.RandomSelectionStrategy(),
        data_model.SelectionStrategyEnum.far_allocation: selection_strategy.FarSelectionStrategy(),
        data_model.SelectionStrategyEnum.near_allocation: selection_strategy.CloseSelectionStrategy(),
    }[config_data.select_strategy]

    size_strategy_func_ = {
        data_model.CapacityStrategyEnum.default: sizing_strategy.DefaultSizingStrategy,
        data_model.CapacityStrategyEnum.peakmultiplier: sizing_strategy.PeakMultiplierSizingStrategy,
    }[config_data.sizing_strategy]

    size_strategy_input_ = {
        data_model.CapacityStrategyEnum.default: config_data.default_sizing_input,
        data_model.CapacityStrategyEnum.peakmultiplier: config_data.peakmult_sizing_input,
    }[config_data.sizing_strategy]
    size_strategy_ = size_strategy_func_(size_strategy_input_)
    
    simulator = opendss.OpenDSSSimulator(config_data.master_file)
    list_of_customers = dss_util.get_list_of_customer_models(simulator.dss_instance, 1)
    mapper_object = dss_util.get_load_mapper_objects(simulator.dss_instance)

    pvscenarios = pv_scenario.create_pv_scenarios(
        list_of_customers, select_strategy_, size_strategy_, config_data.basic_config
    )
    writer_object = opendss_writer.OpenDSSPVScenarioWriter(
        pvscenarios, config_data.output_folder
    )
    writer_object.write(mapper_object)
