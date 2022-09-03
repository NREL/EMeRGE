""" Module for managing deployment strategies."""

import abc
from turtle import distance
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
    ):
        """Abstract method for returning the selection order."""


class RandomSelectionStrategy(SelectionStrategy):
    """Implements random selection strategy."""

    def return_selection_order(
        self, list_of_customers: List[data_model.CustomerModel]
    ):
        random.shuffle(list_of_customers)
        return list_of_customers


class CloseSelectionStrategy(SelectionStrategy):
    """Implements close to feeder selection strategy."""

    def return_selection_order(
        self, list_of_customers: List[data_model.CustomerModel]
    ):
        return sorted(list_of_customers, key=lambda d: d.distance)


class FarSelectionStrategy(SelectionStrategy):
    """Implements far from feeder selection strategy."""

    def return_selection_order(
        self, list_of_customers: List[data_model.CustomerModel]
    ):
        return sorted(list_of_customers, key=lambda d: d.distance, reverse=True)
