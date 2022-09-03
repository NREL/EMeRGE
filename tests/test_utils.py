""" Module for handling testing of utility functions. """

from pathlib import Path

import pandas as pd

from emerge.utils import dss_util
from emerge.simulator import opendss
from emerge.api import utils


def test_bus_distance_dataframe():
    """Test function for checking computation
    of bus distance dataframe."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    bus_distance_df = dss_util.get_bus_distance_dataframe(
        simulator.dss_instance
    )

    assert isinstance(bus_distance_df, pd.DataFrame)


def test_get_list_of_customer_models():
    """Test function for getting list of customer models."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    customer_models = dss_util.get_list_of_customer_models(
        simulator.dss_instance
    )



def test_get_load_mapper_objects():
    """Test function for getting load mapper objects."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / "examples" / "opendss" / "master.dss"

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    mapper_objects = dss_util.get_load_mapper_objects(simulator.dss_instance)



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

def test_get_transformer_customers():
    """ Test function for `get_transformer_customers`
    utility function."""

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    xfmr_customers_df = dss_util.get_transformer_customers(
        simulator.dss_instance
    )

    assert isinstance(xfmr_customers_df, pd.DataFrame)

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
    """ Test function for getting mapping between bus and load flag. """

    root_path = Path(__file__).absolute().parents[1]
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'

    simulator = opendss.OpenDSSSimulator(master_dss_file)
    is_bus_load_df = dss_util.get_bus_load_flag(
        simulator.dss_instance
    )
    assert is_bus_load_df.sum()['is_load'] == simulator.dss_instance.Loads.Count()


def test_buses_coordinate_mapping():
    """ Test function for getting  buses coordinate mapping. """

    geojson_path = Path(__file__).absolute().parents[0] / 'data' / 'geojsons'
    bus_to_coordinate_mapping = utils.buses_coordinate_mapping(geojson_path / 'buses.json')
    assert isinstance(bus_to_coordinate_mapping, dict)

def test_lines_coordinate_mapping():
    """ Test function for getting lines coordinate mapping. """

    geojson_path = Path(__file__).absolute().parents[0] / 'data' / 'geojsons'
    lines_to_coordinate_mapping = utils.lines_coordinate_mapping(geojson_path / 'lines.json')
    assert isinstance(lines_to_coordinate_mapping, dict)

def test_transformer_coordinate_mapping():
    """ Test function for getting transformer coordinate mapping. """

    geojson_path = Path(__file__).absolute().parents[0] / 'data' / 'geojsons'
    xfmr_to_coordinate_mapping = utils.transformer_coordinate_mapping(geojson_path / 'transformers.json')
    assert isinstance(xfmr_to_coordinate_mapping, dict)

def test_getting_map_center():
    """ Test function for getting map center. """

    geojson_path = Path(__file__).absolute().parents[0] / 'data' / 'geojsons'
    map_center = utils.get_map_center(geojson_path / 'buses.json')
    assert isinstance(map_center, dict)
