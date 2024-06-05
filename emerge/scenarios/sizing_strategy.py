"""Module for managing pv sizing strategies when creating
solar scenarios. """

import abc
from typing import Union, Dict, Optional, Tuple

import numpy as np

from emerge.scenarios.data_model import (
    EnergyBasedSolarSizingStrategyInput,
    CustomerModel,
    CapacityStrategyEnum,
    SizeWithProbabilityModel,
)


def _get_value_from_proability(config: Optional[SizeWithProbabilityModel]):
    """Returns specific value from size with probability model."""

    if config is None:
        raise ValueError(f"Input can not be null >> {config}")

    return (
        config.sizes
        if isinstance(config.sizes, float)
        else np.random.choice(config.sizes, p=config.probabilites)
    )


# pylint: disable=too-few-public-methods
class SizingStrategy(abc.ABC):
    """Abstract class for sizing strategy."""

    @abc.abstractmethod
    def return_kw_and_profile(self, customer: CustomerModel) -> Optional[Tuple[float, str]]:
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

    def return_kw_and_profile(self, customer: CustomerModel) -> Optional[Tuple[float, str]]:
        def _return_size(load_kw: float, _config: EnergyBasedSolarSizingStrategyInput):
            return round(
                (load_kw * _config.load_factor * _config.max_pct_production)
                / (100 * _config.capacity_factor),
                3,
            )

        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                print(f"{customer.cust_type} missing from config data {self.config}")
                return (None, None)
            (
                _return_size(customer.kw, self.config.get(customer.cust_type)),
                self.config.get(customer.cust_type).profile,
            )
        (_return_size(customer.kw, self.config), self.config.profile)


class PeakMultiplierSizingStrategy(SizingStrategy):
    """Peak multiplier strategy multiplier peak kw with user defined
    multiplier to get the DER size. e.g. ReOpt suggested solar multiplier."""

    def __init__(
        self,
        config: Union[
            SizeWithProbabilityModel,
            Dict[str, SizeWithProbabilityModel],
        ],
    ):
        self.config = config

    def return_kw_and_profile(
        self,
        customer: CustomerModel,
    ) -> Optional[Tuple[float, str]]:
        def _get_kw_and_profile(config: Optional[SizeWithProbabilityModel]):
            multiplier = _get_value_from_proability(config)
            profile = (
                dict(zip(config.sizes, config.profile)).get(multiplier)
                if isinstance(config.profile, list)
                else config.profile
            )

            return (round(customer.kw * multiplier, 3), profile)

        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                print(f"{customer.cust_type} missing from config data {self.config}")
                return (None, None)
            return _get_kw_and_profile(self.config.get(customer.cust_type))

        return _get_kw_and_profile(self.config)


class FixedSizingStrategy(SizingStrategy):
    """Fixed sizing strategy uses fixed kw with user defined
    value to get the DER size. e.g. Level 1 EV charger"""

    def __init__(
        self,
        config: Union[
            SizeWithProbabilityModel,
            Dict[str, SizeWithProbabilityModel],
        ],
    ):
        self.config = config

    def return_kw_and_profile(
        self,
        customer: CustomerModel,
    ) -> Optional[Tuple[float, str]]:
        def _get_kw_and_profile(config: Optional[SizeWithProbabilityModel]):
            fixed_value = _get_value_from_proability(config)
            profile = (
                dict(zip(config.sizes, config.profile)).get(fixed_value)
                if isinstance(config.profile, list)
                else config.profile
            )

            return (fixed_value, profile)

        if isinstance(self.config, dict):
            if customer.cust_type not in self.config:
                print(f"{customer.cust_type} missing from config data {self.config}")
                return (None, None)
            return _get_kw_and_profile(self.config.get(customer.cust_type))

        return _get_kw_and_profile(self.config)


SIZING_STRATEGY_MAPPER = {
    CapacityStrategyEnum.solar_energy_based: EnergyBasedSolarSizingStrategy,
    CapacityStrategyEnum.peak_multiplier: PeakMultiplierSizingStrategy,
    CapacityStrategyEnum.fixed_sizing: FixedSizingStrategy,
}
