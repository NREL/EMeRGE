""" Module for generating PV deployment scenarios.

A PV deployment scenario is a hypothetical scenario defined on top
of base distribution system model that uses some rules/forecast/expertise
to come up with number, size and location of solar units to be installed.
This is then can be used in various analysis. 
"""

from typing import List

from emerge.scenarios import data_model
from emerge.scenarios import selection_strategy, sizing_strategy


def _get_sizing_func_input(item: data_model._DERScenarioInput):
    return {
        data_model.CapacityStrategyEnum.solar_energy_based: item.energy_sizing_input,
        data_model.CapacityStrategyEnum.peak_multiplier: item.peakmult_sizing_input,
        data_model.CapacityStrategyEnum.fixed_sizing: item.fixed_sizing_input
    }.get(item.sizing_strategy)


def _add_other_ders(
    ders_list: List[data_model.BasicDERModel],
    strategy: sizing_strategy.SizingStrategy,
    der_type: data_model.DERType 
)-> List[data_model.BasicDERModel]:
    """Add other ders on top of existing der for a customer.

    Args:
        ders_list (List[data_model.BasicDERModel]): List of already existing DERs
        strategy (sizing_strategy.SizingStrategy): Strategy for coming up with the DER size
        der_type (data_model.DERType): DERType to be added
    """

    der_models = []

    for der in ders_list:
        if der.der_type == der_type:
            # pylint: disable=broad-exception-raised
            raise Exception(f'DER type can not be same when adding other ders! {der} >> {der_type}')
        
        der_models.append(
            data_model.BasicDERModel(
                    name=der.name + f'_{der_type}',
                    kw=strategy.return_size_in_kw(der.customer),
                    customer=der.customer,
                    der_type=der_type
                )
        )
    return der_models


def _get_ders(
    customers: List[data_model.CustomerModel],
    target_kw: float,
    strategy: sizing_strategy.SizingStrategy,
    der_type: data_model.DERType
) -> List[data_model.BasicDERModel]:
    """Creates a list of der systems for a target kw.

    Args:
        customers (List[data_model.CustomerModel]): List of customers models
        target_kw (float): Target kW
        strategy (sizing_strategy.SizingStrategy): Strategy for coming up with the DER size
        der_type (data_model.DERType): DERType to be added
    """

    if not customers:
        return []

    der_models = []
    for customer in customers:
        if target_kw <= 0:
            break

        der_capacity = strategy.return_size_in_kw(customer)

        if der_capacity and der_capacity > 0:
            der_capacity = min(der_capacity, target_kw)

            target_kw -= der_capacity
            der_models.append(
                data_model.BasicDERModel(
                    name=customer.name + "_der",
                    kw=der_capacity,
                    customer=customer,
                    der_type=der_type
                )
            )

    return der_models


# pylint: disable=too-many-locals
def create_der_scenarios(
    list_of_customers: List[data_model.CustomerModel],
    scenario_config: data_model.ScenarioConfig,
    der_config: data_model.DERScenarioInput
) -> List[data_model.DistDERScenarioModel]:
    """Function for creating distributed DER scenarios
    for distribution system.

    Args:
        list_of_loads (List[data_model.CustomerModel]): List of customer for
                scenario generation.
        scenario_config (data_model.ScenarioConfig): Configuration data for
                generating scenarios
        der_types List[data_model.DERType]: DER types to be added for a load
    Returns:
        List[data_model.DistDERScenarioModel]: List of `DistDERScenarioModel`
            models.
    """

    select_strategy = selection_strategy.SELECTION_STRATEGY_MAPPER[
        der_config.selection_strategy]()
    
    scenarios: List[data_model.DistDERScenarioModel] = []

    # Get total load
    total_load_kw = sum(load.kw for load in list_of_customers)

    # loop over all the samples and pv penetrations
    for sample_id in range(scenario_config.max_num_of_samples):
        # Idea is to keep pv systems installed in previous penetrations
        past_ders: List[data_model.BasicDERModel] = []
        past_capacity = 0

        for der_penetration_id in range(1, scenario_config.num_of_penetration + 1):
            
            der_capacity = (
                der_penetration_id * scenario_config.pct_resolution / 100
            ) * total_load_kw

            previous_loads = list(set([der.customer.name for der in past_ders]))
            loads_without_der = [
                load for load in list_of_customers if load.name not in previous_loads
            ]

            # Returns order in which load is to be selected to add pv
            loads = select_strategy.return_selection_order(
                list_of_customers=loads_without_der
            )
            
            sizing_strategy_object = sizing_strategy.SIZING_STRATEGY_MAPPER.get(
                der_config.sizing_strategy
            )(_get_sizing_func_input(der_config))


            main_der_models = _get_ders(loads, der_capacity - past_capacity, 
                                   sizing_strategy_object, der_config.der_type)
            
            other_der_models = []
            for other_der in der_config.other_ders:
                sizing_strategy_object = sizing_strategy.SIZING_STRATEGY_MAPPER.get(
                    other_der.sizing_strategy
                )(_get_sizing_func_input(other_der))
                other_der_models += _add_other_ders(main_der_models, 
                                   sizing_strategy_object, other_der.der_type)
            
            scenario = data_model.DistDERScenarioModel(
                name=f"scenario_{sample_id}_"
                f"{int(der_penetration_id*scenario_config.pct_resolution)}",
                sample_id=sample_id,
                penetration=round(der_capacity, 3),
                ders=past_ders + main_der_models + other_der_models,
            )

            past_capacity += der_capacity
            past_ders = past_ders + main_der_models + other_der_models

            scenarios.append(scenario)

    return scenarios
