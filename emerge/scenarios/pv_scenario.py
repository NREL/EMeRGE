""" Module for generating PV deployment scenarios.

A PV deployment scenario is a hypothetical scenario defined on top
of base distribution system model that uses some rules/forecast/expertise
to come up with number, size and location of solar units to be installed.
This is then can be used in various analysis. 
"""

from typing import List

from emerge.scenarios import data_model
from emerge.scenarios import selection_strategy, sizing_strategy


def _get_pvs(
    customers: List[data_model.CustomerModel],
    target_kw: float,
    strategy: sizing_strategy.SizingStrategy,
) -> List[data_model.PVModel]:
    """Creates a list of pv systems for a target kw.

    Args:
        customers (List[data_model.CustomerModel]): List of customers models
        target_kw (float): Target PV kW
    """

    if not customers:
        return []

    pv_models = []
    for customer in customers:
        if target_kw <= 0:
            break

        pv_capacity = strategy.return_pv_size_in_kw(customer)
        pv_capacity = min(pv_capacity, target_kw)

        target_kw -= pv_capacity
        pv_models.append(
            data_model.PVModel(
                name=customer.name + "_pv",
                kw=pv_capacity,
                customer=customer.name,
            )
        )

    return pv_models


# pylint: disable=too-many-locals
def create_pv_scenarios(
    list_of_customers: List[data_model.CustomerModel],
    select_strategy: selection_strategy.SelectionStrategy,
    size_strategy: sizing_strategy.SizingStrategy,
    scenario_config: data_model.PVScenarioConfig,
) -> List[data_model.DistPVScenarioModel]:
    """Function for creating distributed pv scenarios
    for distribution system.

    Args:
        list_of_loads (List[data_model.CustomerModel]): List of customer for
                scenario generation.
        selection_strategy (selection_strategy.SelectionStrategy): Selection strategy object
        selection_strategy (sizing_strategy.SizingStrategy): Sizing strategy object
        scenario_config (data_model.PVScenarioConfig): Configuration data for
                generating scenarios
    Returns:
        List[data_model.DistPVScenarioModel]: List of `DistPVScenarioModel`
            models.
    """

    scenarios = []

    # Get total load
    total_load_kw = sum(load.kw for load in list_of_customers)

    # loop over all the samples and pv penetrations
    for sample_id in range(scenario_config.max_num_of_samples):
        # Idea is to keep pv systems installed in previous penetrations
        past_pvs: List[data_model.PVModel] = []
        past_capacity = 0

        for pv_penetration_id in range(1, scenario_config.num_of_penetration + 1):
            pv_capacity = (
                pv_penetration_id * scenario_config.pct_resolution / 100
            ) * total_load_kw

            previous_loads = [pv.customer for pv in past_pvs]
            loads_without_pv = [
                load for load in list_of_customers if load.name not in previous_loads
            ]

            # Returns order in which load is to be selected to add pv
            loads = select_strategy.return_selection_order(
                list_of_customers=loads_without_pv
            )
            pv_models = _get_pvs(loads, pv_capacity - past_capacity, size_strategy)

            scenario = data_model.DistPVScenarioModel(
                name=f"scenario_{sample_id}_"
                f"{int(pv_penetration_id*scenario_config.pct_resolution)}",
                sample_id=sample_id,
                pv_penetration=round(pv_capacity, 3),
                pvs=past_pvs + pv_models,
            )

            past_capacity = pv_capacity
            past_pvs += pv_models

            scenarios.append(scenario)

    return scenarios
