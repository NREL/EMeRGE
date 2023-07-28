"""Module for storing configuration for cli interfaces"""

from typing import Dict, List

# pylint: disable=no-name-in-module
from pydantic import BaseModel
from emerge.scenarios.data_model import (
    ScenarioConfig,
    SelectionStrategyEnum,
    _DERScenarioInput
)

# pylint: disable=too-few-public-methods

class _DERCliScenarioInputModel(_DERScenarioInput):
    """ Interface for base der scenario model. """
    tag_name: str

class DERCliScenarioInputModel(_DERCliScenarioInputModel):
    """ Interface for der scenario input model. """
    file_name: str
    selection_strategy: SelectionStrategyEnum
    other_ders: List[_DERCliScenarioInputModel]


class PVSceanarioCliInputModel(BaseModel):
    """CLI interface model for generating solar scenarios."""

    master_file: str
    output_folder: str
    basic_config: ScenarioConfig
    der_scenario: List[DERCliScenarioInputModel]
    
