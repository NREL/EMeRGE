""" Module for handling testing of utility functions. """

from pathlib import Path

from emerge.utils import dss_util
from emerge.simulator import opendss
import pandas as pd

def test_get_line_customers():
    """ Test function for `get_line_customers` 
    utility function."""

    root_path = Path(__file__).absolute().parents[1] 
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    line_customers_df = dss_util.get_line_customers(
        simulator.dss_instance
    )

    assert isinstance(line_customers_df, pd.DataFrame)

def test_get_source_node():
    """ test function for getting source node. """
    root_path = Path(__file__).absolute().parents[1] 
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    source_node = dss_util.get_source_node(
        simulator.dss_instance
    )
    assert source_node == '80_27834864364979_13_0915193376659_htnode'

def test_get_bus_load_flag():
    root_path = Path(__file__).absolute().parents[1] 
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    is_bus_load_df = dss_util.get_bus_load_flag(
        simulator.dss_instance
    )
    assert is_bus_load_df.sum()['is_load'] == simulator.dss_instance.Loads.Count()