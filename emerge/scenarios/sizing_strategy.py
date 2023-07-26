"""Module for managing pv sizing strategies when creating
solar scenarios. """

import abc
from typing import Union, Dict
from emerge.scenarios.data_model import (
    DefaultCapacityStrategyInput,
    PeakMultiplierCapacityStrategyInput,
    CustomerModel,
)


# pylint: disable=too-few-public-methods
class SizingStrategy(abc.ABC):
    """Abstract class for sizing strategy."""

    @abc.abstractmethod
    def return_pv_size_in_kw(self, customer: CustomerModel) -> float:
        """Abstract method for returning solar size."""


class DefaultSizingStrategy(SizingStrategy):
    """Default strategy is to size solar system based on
    load factor, solar capacity factor and percentage energy
    to be replaced by solar annually."""

    def __init__(
        self,
        config: Union[
            DefaultCapacityStrategyInput, Dict[str, DefaultCapacityStrategyInput]
        ],
    ):
        self.config = config

    def return_pv_size_in_kw(self, customer: CustomerModel) -> float:
        def _return_size(load_kw: float, _config: DefaultCapacityStrategyInput):
            return round(
                (load_kw * _config.load_factor * _config.max_pct_production)
                / (100 * _config.capacity_factor),
                3,
            )

        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                raise KeyError(
                    f"{customer.cust_type}" f"missing from config data {self.config}"
                )
            _return_size(customer.kw, self.config.get(customer.cust_type))
        _return_size(customer.kw, self.config)


class PeakMultiplierSizingStrategy(SizingStrategy):
    """Peak multiplier strategy multiplier peak kw with user defined
    multiplier to get the solar size. e.g. ReOpt suggested solar multiplier."""

    def __init__(
        self,
        config: Union[
            PeakMultiplierCapacityStrategyInput,
            Dict[str, PeakMultiplierCapacityStrategyInput],
        ],
    ):
        self.config = config

    def return_pv_size_in_kw(
        self,
        customer: CustomerModel,
    ):
        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                raise KeyError(
                    f"{customer.cust_type}" f"missing from config data {self.config}"
                )
            return round(
                customer.kw * self.config.get(customer.cust_type).multiplier, 3
            )
        return round(customer.kw * self.config.multiplier, 3)
