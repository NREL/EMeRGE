""" Module for handling testing of utility functions. """

from pathlib import Path

import pandas as pd

from emerge.utils import dss_util
from emerge.simulator import opendss


def test_bus_distance_dataframe():
    """Test function for checking computation
    of bus distance dataframe."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    bus_distance_df = dss_util.get_bus_distance_dataframe()

    assert isinstance(bus_distance_df, pd.DataFrame)


def test_get_list_of_customer_models():
    """Test function for getting list of customer models."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    dss_util.get_list_of_customer_models()


def test_get_load_mapper_objects():
    """Test function for getting load mapper objects."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    dss_util.get_load_mapper_objects()


def test_get_line_customers():
    """Test function for `get_line_customers`
    utility function."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    line_customers_df = dss_util.get_line_customers()

    assert isinstance(line_customers_df, pd.DataFrame)


def test_get_transformer_customers():
    """Test function for `get_transformer_customers`
    utility function."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    xfmr_customers_df = dss_util.get_transformer_customers()

    assert isinstance(xfmr_customers_df, pd.DataFrame)


def test_get_source_node():
    """test function for getting source node."""
    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    opendss.OpenDSSSimulator(master_dss_file)
    source_node = dss_util.get_source_node()
    assert source_node == "80_27834864364979_13_0915193376659_htnode"


def test_get_bus_load_flag():
    """Test function for getting mapping between bus and load flag."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    is_bus_load_df = dss_util.get_bus_load_flag()
    assert is_bus_load_df.sum()["is_load"] == simulator.dss_instance.Loads.Count()
