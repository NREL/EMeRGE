""" Utility functions for dss_instance. """

import copy
from typing import List

import opendssdirect as dss
import pandas as pd
import networkx as nx

from emerge.metrics.exceptions import EnergyMeterNotDefined
from emerge.network import asset_metrics
from emerge.scenarios import data_model


def get_bus_distance_dataframe(dss_instance: dss)-> pd.DataFrame:
    """Get bus distance dataframe.
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        pd.DataFrame: Dataframe containing distance from 
            substation indexed by busname.
    
    """

    bus_distance_df = {"busname": [], "distance": []}
    for bus in dss_instance.Circuit.AllBusNames():
        dss_instance.Circuit.SetActiveBus(bus)

        bus_distance_df["busname"].append(bus)
        bus_distance_df["distance"].append(dss_instance.Bus.Distance())

    if not sum(bus_distance_df["distance"]):
        raise EnergyMeterNotDefined(
            "Define energy meter to be able to find"
            "number of customers downward of line segment."
        )
    return pd.DataFrame(bus_distance_df).set_index("busname")


def get_list_of_customer_models(
        dss_instance: dss, 
        load_multiplier=1.0,
        cust_type: str = "yearly"
    ) -> List[data_model.CustomerModel]:
    """Returns list of customer models from dss instance.
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        List[data_model.CustomerModel]: List of customer data
            model.
    """
    cust_type_func = {
        "class": dss_instance.Loads.Class,
        "yearly": dss_instance.Loads.Yearly
    }.get(cust_type)

    flag = dss_instance.Loads.First()
    bus_distance_df = get_bus_distance_dataframe(dss_instance)
    customer_model = []
    while flag:
        busname = dss_instance.CktElement.BusNames()[0].split('.')[0]
        customer_model.append(
            data_model.CustomerModel(
                name=dss_instance.CktElement.Name(),
                kw=dss_instance.Loads.kW()*load_multiplier,
                distance=bus_distance_df.loc[busname]['distance'],
                cust_type=str(cust_type_func())
            )
        )

        flag = dss_instance.Loads.Next()

    return customer_model


def get_load_mapper_objects(dss_instance: dss)-> List[data_model.LoadMetadataModel]:
    """Returns list of load mapper object models.
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        List[data_model.LoadMetadataModel]: List of load
            metadata model.
    """

    flag = dss_instance.Loads.First()
    mapper_model = []
    while flag:
        mapper_model.append(
            data_model.LoadMetadataModel(
                name=dss_instance.CktElement.Name(),
                bus=dss_instance.CktElement.BusNames()[0],
                num_phase=dss_instance.Loads.Phases(),
                kv=dss_instance.Loads.kV(),
                yearly=dss_instance.Loads.Yearly()
            )
        )

        flag = dss_instance.Loads.Next()

    return mapper_model


def get_bus_load_dataframe(dss_instance: dss)-> pd.DataFrame:
    """Bus to load mapping dataframe.
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        pd.DataFrame: Dataframe containing mapping between load
            name and bus name
    """

    flag = dss_instance.Loads.First()
    load_bus_name_dict = {"busname": [], "loadname": []}
    while flag:

        load_name = dss_instance.CktElement.Name()
        busname = dss_instance.CktElement.BusNames()[0].split(".")[0]
        load_bus_name_dict["busname"].append(busname)
        load_bus_name_dict["loadname"].append(load_name)

        flag = dss_instance.Loads.Next()

    return pd.DataFrame(load_bus_name_dict)


def get_bus_load_flag(dss_instance: dss) -> pd.DataFrame:
    """Bus to load mapping dataframe.

    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        pd.DataFrame: Dataframe containing load flag
            indexed by bus name.
    """

    load_bus_df = get_bus_load_dataframe(dss_instance)
    buses_with_load = list(load_bus_df["busname"])
    all_buses = dss_instance.Circuit.AllBusNames()
    buses_without_load = list(set(all_buses) - set(buses_with_load))
    is_bus_load = {
        "busname": buses_with_load + buses_without_load,
        "is_load": [1] * len(buses_with_load) + [0] * len(buses_without_load),
    }

    return pd.DataFrame(is_bus_load).set_index("busname")


def get_line_customers(dss_instance: dss) ->pd.DataFrame:
    """Function to retrieve dataframe containing number
    of downward serving customers for all line segments.

    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        pd.DataFrame: Dataframe containing number of customers
            indexed by line name.
    """
    line_customers_df = {"linename": [], "customers": []}

    dss_instance.Circuit.SetActiveClass("Line")
    flag = dss_instance.ActiveClass.First()

    while flag:
        line_name = dss_instance.CktElement.Name().lower()
        n_customers = dss_instance.Lines.TotalCust()
        line_customers_df["linename"].append(line_name)
        line_customers_df["customers"].append(n_customers)
        flag = dss_instance.ActiveClass.Next()

    if not any(line_customers_df["customers"]):
        raise EnergyMeterNotDefined(
            "Define energy meter to be able to find"
            "number of customers downward of line segment."
        )
    return pd.DataFrame(line_customers_df).set_index("linename")


def get_transformer_customers(dss_instance: dss)-> pd.DataFrame:
    """Function to retrieve dataframe containing number
    of downward serving customers for all transformers.

    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        pd.DataFrame: Dataframe containing number of customers
            indexed by transformer name.
    """
    xfmr_customers_df = {"transformername": [], "customers": []}

    network = asset_metrics.networkx_from_opendss_model(dss_instance)
    substation_bus = get_source_node(dss_instance)
    bus_load_flag_df = get_bus_load_flag(dss_instance)

    dss_instance.Circuit.SetActiveClass("Transformer")
    flag = dss_instance.ActiveClass.First()

    while flag:
        network_copy = copy.deepcopy(network)
        xmfr_name = dss_instance.CktElement.Name().lower()

        edge_to_be_removed = []
        for edge in network_copy.edges():
            edge_data = network_copy.get_edge_data(*edge)
            if (
                edge_data
                and "name" in edge_data
                and edge_data["name"] == xmfr_name
            ):
                edge_to_be_removed.append(edge)

        network_copy.remove_edges_from(edge_to_be_removed)
        connected_buses = nx.node_connected_component(
            network_copy, substation_bus
        )

        filtered_bus_df = bus_load_flag_df.loc[
            bus_load_flag_df.index.difference(connected_buses)
        ]

        n_customers = filtered_bus_df.sum()["is_load"]
        xfmr_customers_df["transformername"].append(xmfr_name)
        xfmr_customers_df["customers"].append(n_customers)
        flag = dss_instance.ActiveClass.Next()

    return pd.DataFrame(xfmr_customers_df).set_index("transformername")


def get_source_node(dss_instance: dss) -> str:

    """Function to return source node for dss model.
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect

    Returns:
        str: Name of the source node
    """

    df = dss_instance.utils.class_to_dataframe("vsource")
    source_node = df["bus1"].tolist()[0].split(".")[0]
    return source_node
