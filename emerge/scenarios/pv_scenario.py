""" Module for generating PV deployment scenarios.

A PV deployment scenario is a hypothetical scenario defined on top
of base distribution system model that uses some rules/forecast/expertise
to come up with number, size and location of solar units to be installed.
This is then can be used in various analysis. 
"""

import abc
from typing import List

from emerge.scenarios import data_model
from emerge.scenarios import strategy


class PVScenarioGenerator(abc.ABC):
    """Class responsible for generating PV scenarios."""


class DistributedPVScenario(PVScenarioGenerator):
    """ " Class for generating distributed PV scenarios.

    Distributed PV are typically installed in customers premise. This class
    will take list of loads/customers and creates scenario based on different
    strategy.

    Attributes:
        list_of_loads (List[data_model.CustomerModel]): List of customer for
                scenario generation.
    """

    def __init__(
        self,
        list_of_customers: List[data_model.CustomerModel],
        scenario_config: data_model.PVScenarioConfig,
    ) -> None:
        """Constructor for `DistributedPVScenario` class.

        Args:
            list_of_customers (List[data_model.CustomerModel]): List of customer for
                scenario generation.
            scenario_config (data_model.PVScenarioConfig): Configuration data for
                generating scenarios
        """

        self.list_of_customers = list_of_customers
        self.scenario_config = scenario_config

    def _get_pvs(
        self, customers: List[data_model.CustomerModel], target_kw: float
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

            pv_capacity = round(
                (
                    customer.kw
                    * self.scenario_config.load_factor
                    * self.scenario_config.max_pct_production
                )
                / (100 * self.scenario_config.capacity_factor),
                3,
            )

            if pv_capacity > target_kw:
                pv_capacity = target_kw

            target_kw -= pv_capacity
            pv_models.append(
                data_model.PVModel(
                    name=customer.name + "_pv",
                    kw=pv_capacity,
                    customer=customer.name,
                )
            )

        return pv_models

    def create_pv_scenarios_for_feeder(
        self, selection_strategy: strategy.SelectionStrategy
    ) -> List[data_model.DistPVScenarioModel]:
        """Creates a scenario based on strategy passed.

        Args:
            selection_strategy (strategy.SelectionStrategy): Selection strategy object
        """

        scenarios = []

        # Get total load
        total_load_kw = sum(load.kw for load in self.list_of_customers)

        # loop over all the samples and pv penetrations
        for sample_id in range(self.scenario_config.max_num_of_samples):

            # Idea is to keep pv systems installed in previous penetrations
            past_pvs, past_capacity = [], 0
            for pv_penetration_id in range(
                1, self.scenario_config.num_of_penetration + 1
            ):

                pv_capacity = (
                    pv_penetration_id
                    * self.scenario_config.pct_resolution
                    / 100
                ) * total_load_kw

                previous_loads = [pv.customer for pv in past_pvs]
                loads_without_pv = [
                    load
                    for load in self.list_of_customers
                    if load.name not in previous_loads
                ]

                # Returns order in which load is to be selected to add pv
                loads = selection_strategy.return_selection_order(
                    list_of_customers=loads_without_pv
                )
                pv_models = self._get_pvs(loads, pv_capacity - past_capacity)

                scenario = data_model.DistPVScenarioModel(
                    name=f"scenario_{sample_id}_{int(pv_penetration_id*self.scenario_config.pct_resolution)}",
                    sample_id=sample_id,
                    pv_penetration=round(pv_capacity,3),
                    pvs=past_pvs + pv_models,
                )

                past_capacity = pv_capacity
                past_pvs += pv_models

                scenarios.append(scenario)

        return scenarios
