"""Module for storing configuration for cli interfaces"""

from typing import Dict, Union, Optional

# pylint: disable=no-name-in-module
from pydantic import BaseModel
from emerge.scenarios.data_model import (
    PVScenarioConfig,
    SelectionStrategyEnum,
    CapacityStrategyEnum,
    DefaultCapacityStrategyInput,
    PeakMultiplierCapacityStrategyInput
)


# pylint: disable=too-few-public-methods
class PVSceanarioCliInputModel(BaseModel):
    """CLI interface model for generating solar scenarios."""

    master_file: str
    output_folder: str
    basic_config: PVScenarioConfig
    select_strategy: SelectionStrategyEnum
    sizing_strategy: CapacityStrategyEnum
    default_sizing_input:  Dict[str,DefaultCapacityStrategyInput] | DefaultCapacityStrategyInput | None = None
    peakmult_sizing_input: Dict[str,PeakMultiplierCapacityStrategyInput] | PeakMultiplierCapacityStrategyInput | None = None
    
