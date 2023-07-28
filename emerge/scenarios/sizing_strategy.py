"""Module for managing pv sizing strategies when creating
solar scenarios. """

import abc
from typing import Union, Dict, Optional
from emerge.scenarios.data_model import (
    EnergyBasedSolarSizingStrategyInput,
    CustomerModel,
    CapacityStrategyEnum
)


# pylint: disable=too-few-public-methods
class SizingStrategy(abc.ABC):
    """Abstract class for sizing strategy."""

    @abc.abstractmethod
    def return_size_in_kw(self, customer: CustomerModel) -> Optional[float]:
        """Abstract method for returning size."""


class EnergyBasedSolarSizingStrategy(SizingStrategy):
    """Default strategy is to size solar based on
    load factor, solar capacity factor and percentage energy
    to be replaced by solar annually."""

    def __init__(
        self,
        config: Union[
            EnergyBasedSolarSizingStrategyInput, Dict[str, EnergyBasedSolarSizingStrategyInput]
        ],
    ):
        self.config = config

    def return_size_in_kw(self, customer: CustomerModel) -> float:
        def _return_size(load_kw: float, _config: EnergyBasedSolarSizingStrategyInput):
            return round(
                (load_kw * _config.load_factor * _config.max_pct_production)
                / (100 * _config.capacity_factor),
                3,
            )

        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                print(
                    f"{customer.cust_type}" f"missing from config data {self.config}"
                )
                return
            _return_size(customer.kw, self.config.get(customer.cust_type))
        _return_size(customer.kw, self.config)


class PeakMultiplierSizingStrategy(SizingStrategy):
    """Peak multiplier strategy multiplier peak kw with user defined
    multiplier to get the DER size. e.g. ReOpt suggested solar multiplier."""

    def __init__(
        self,
        config: Union[
            float,
            Dict[str, float],
        ],
    ):
        self.config = config

    def return_size_in_kw(
        self,
        customer: CustomerModel,
    ):
        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                print(
                    f"{customer.cust_type}" f"missing from config data {self.config}"
                )
                return
            return round(
                customer.kw * self.config.get(customer.cust_type), 3
            )
        return round(customer.kw * self.config, 3)
    
class FixedSizingStrategy(SizingStrategy):
    """Fixed sizing strategy uses fixed kw with user defined
    value to get the DER size. e.g. Level 1 EV charger"""

    def __init__(
        self,
        config: Union[
            float,
            Dict[str, float],
        ],
    ):
        self.config = config

    def return_size_in_kw(
        self,
        customer: CustomerModel,
    ):
        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                print(
                    f"{customer.cust_type}" f"missing from config data {self.config}"
                )
                return
            return round(
                self.config.get(customer.cust_type), 3
            )
        return round(customer.kw, 3)
    

SIZING_STRATEGY_MAPPER  ={
    CapacityStrategyEnum.solar_energy_based: EnergyBasedSolarSizingStrategy,
    CapacityStrategyEnum.peak_multiplier: PeakMultiplierSizingStrategy,
    CapacityStrategyEnum.fixed_sizing: FixedSizingStrategy
}
