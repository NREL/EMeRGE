""" This module contains test function for testing the
feature included in `powerflow_metrics_powerflow` module."""

from pathlib import Path

import pandas as pd

from emerge.metrics import powerflow_metrics_opendss
from emerge.simulator import opendss


def test_get_voltage_by_dataframe():
    """ Test function for `get_voltage_by_dataframe` 
    utility function."""

    root_path = Path(__file__).absolute().parents[1] 
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    voltage_df = powerflow_metrics_opendss.get_voltage_dataframe(
        simulator.dss_instance
    )

    assert isinstance(voltage_df, pd.DataFrame)