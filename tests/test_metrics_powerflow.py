""" This module contains test function for testing the
feature included in `powerflow_metrics_powerflow` module."""

from pathlib import Path

import polars as pl
import pandas as pd

from emerge.simulator import powerflow_results
from emerge.simulator import opendss


def test_pv_power_dataframe():
    """Test function for `pv_power_dataframe`
    utility function."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    pv_df = powerflow_results.get_pv_power_dataframe()

    assert isinstance(pv_df, pd.DataFrame)


def test_get_voltage_by_dataframe():
    """Test function for `get_voltage_by_dataframe`
    utility function."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    voltage_df = powerflow_results.get_voltage_dataframe()

    assert isinstance(voltage_df, pl.DataFrame)


def test_get_lineloading_dataframe():
    """Test function for `get_lineloading_dataframe`
    utility function."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    line_loading_df = powerflow_results.get_loading_dataframe()

    assert isinstance(line_loading_df, pl.DataFrame)
