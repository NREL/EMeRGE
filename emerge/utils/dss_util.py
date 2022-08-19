""" Utility functions for dss_instance. """

import opendssdirect as dss
import pandas as pd
from emerge.metrics.exceptions import EnergyMeterNotDefined

def get_bus_load_dataframe(dss_instance:dss):
    """ Bus to load mapping dataframe. """

    flag = dss_instance.Loads.First()
    load_bus_name_dict = {"busname": [], "loadname": []}
    while flag:
        
        load_name = dss_instance.CktElement.Name()
        busname = dss_instance.CktElement.BusNames()[0].split('.')[0]
        load_bus_name_dict["busname"].append(busname)
        load_bus_name_dict["loadname"].append(load_name)
        
        flag = dss_instance.Loads.Next()

    return pd.DataFrame(load_bus_name_dict)


def get_bus_load_flag(dss_instance:dss):
    """ Bus to load mapping dataframe. """

    load_bus_df = get_bus_load_dataframe(dss_instance)
    buses_with_load = list(load_bus_df['busname'])
    all_buses = dss_instance.Circuit.AllBusNames()
    buses_without_load = list(set(all_buses) - set(buses_with_load))
    is_bus_load = {"busname": buses_with_load + buses_without_load, 
        "is_load": [1]*len(buses_with_load) + [0]*len(buses_without_load)}
    
    return pd.DataFrame(is_bus_load).set_index("busname")
    

def get_line_customers(dss_instance: dss):
    """ Function to retrieve dataframe containing number
    of downward serving customers for all line segments. 
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect
    """
    line_customers_df = {"linename": [], "customers": []}

    dss_instance.Circuit.SetActiveClass("Line")
    flag = dss_instance.ActiveClass.First()

    while flag:
        line_name = dss_instance.CktElement.Name()
        n_customers = dss_instance.Lines.TotalCust()
        line_customers_df['linename'].append(line_name)
        line_customers_df['customers'].append(n_customers)
        flag = dss_instance.ActiveClass.Next()
    
    if not any(line_customers_df['customers']):
        raise EnergyMeterNotDefined("Define energy meter to be able to find" 
            "number of customers downward of line segment.")
    return pd.DataFrame(line_customers_df).set_index("linename")

def get_source_node(dss_instance: dss):
    
    """ Function to return source node for dss model. """
    df = dss_instance.utils.class_to_dataframe('vsource')
    source_node = df['bus1'].tolist()[0].split('.')[0]
    return source_node
