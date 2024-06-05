""" Module for managing deployment strategies."""

import abc
from typing import List
import random

from emerge.scenarios import data_model


class SelectionStrategy(abc.ABC):
    """Abstract class for selection strategy.

    Idea is to take list of customer models and define
    a order in which they are to be selected for placing
    pvs.
    """

    @abc.abstractmethod
    def return_selection_order(
        self, list_of_customers: List[data_model.CustomerModel]
    ) -> List[data_model.CustomerModel]:
        """Abstract method for returning the selection order.

        Args:
            list_of_customers (List[data_model.CustomerModel]): List
                of `CustomerModel` objects.

        Returns:
            List[data_model.CustomerModel]: List
                of `CustomerModel` objects.
        """


class RandomSelectionStrategy(SelectionStrategy):
    """Implements random selection strategy."""

    def return_selection_order(self, list_of_customers: List[data_model.CustomerModel]):
        """Refer to base class for more details."""
        random.shuffle(list_of_customers)
        return list_of_customers


class CloseSelectionStrategy(SelectionStrategy):
    """Implements close to feeder selection strategy."""

    def return_selection_order(self, list_of_customers: List[data_model.CustomerModel]):
        """Refer to base class for more details."""
        return sorted(list_of_customers, key=lambda d: d.distance)


class FarSelectionStrategy(SelectionStrategy):
    """Implements far from feeder selection strategy."""

    def return_selection_order(self, list_of_customers: List[data_model.CustomerModel]):
        """Refer to base class for more details."""
        return sorted(list_of_customers, key=lambda d: d.distance, reverse=True)


SELECTION_STRATEGY_MAPPER = {
    data_model.SelectionStrategyEnum.random_allocation: RandomSelectionStrategy,
    data_model.SelectionStrategyEnum.far_allocation: FarSelectionStrategy,
    data_model.SelectionStrategyEnum.near_allocation: CloseSelectionStrategy,
}
