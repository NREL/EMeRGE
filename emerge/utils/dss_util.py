""" Utility functions for dss_instance. """

import opendssdirect as dss
import pandas as pd

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