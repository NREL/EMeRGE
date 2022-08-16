

"""
 Extract base level metrics
"""
# standard imports
import logging
import json

# third-party imports
import networkx as nx
import numpy as np
import opendssdirect as dss
import pandas as pd

# internal imports
from emerge.utils.util import setup_logging
from emerge.simulator.opendss import OpenDSSSimulator
from emerge.db.db_handler import TinyDBHandler
from emerge.metrics.feeder_metrics_opendss import networkx_from_opendss_model


def get_allbus_voltage_pu(dss_instance):
    return dss_instance.Circuit.AllBusMagPu()

def get_voltage_distribution(voltage_array:list, 
    bins:list = [0.7 + i*0.05 for i in range(12)]):

    # Remove zeros
    voltage_array = np.array(voltage_array)
    voltage_array = voltage_array[voltage_array !=0]

    hist, _ = np.histogram(voltage_array, bins)
    pct_hist = list(np.array(hist) *100/ len(voltage_array))
    
    return {
        'Voltage bins': bins[:-1],
        'Percentage nodes':  pct_hist
    }

def get_voltage_by_distance(dss_instance):


    mapper = {1: 'Phase A', 2: 'Phase B', 3: 'Phase C'}
    voltage_by_distance = {'Voltage (pu)': [], 'Distance from substation (km)': [], 'Phase': []}
    for phase in range(1,4):
        pu_voltages = dss_instance.Circuit.AllNodeVmagPUByPhase(phase)
        node_distances = dss_instance.Circuit.AllNodeDistancesByPhase(phase)

        voltage_by_distance['Voltage (pu)'].extend(pu_voltages)
        voltage_by_distance['Phase'].extend([mapper[phase]]*len(pu_voltages))
        voltage_by_distance['Distance from substation (km)'].extend(node_distances)

    return voltage_by_distance

def get_voltage_by_lat_lon(dss_instance):

    network = networkx_from_opendss_model(dss_instance)
    node_data = {node[0]: node[1] for node in network.nodes.data()}
    all_bus_voltage = dss_instance.Circuit.AllBusMagPu()
    all_bus_names = dss_instance.Circuit.AllBusNames()

    voltage_by_lat_lon = {
        'longitudes': [],
        'latitudes': [],
        'voltage (pu)': []
    }

    for bus, voltage_pu in zip(all_bus_names, all_bus_voltage):
        voltage_by_lat_lon['latitudes'].append(node_data[bus]['pos'][1])
        voltage_by_lat_lon['longitudes'].append(node_data[bus]['pos'][0])
        voltage_by_lat_lon['voltage (pu)'].append(voltage_pu)
    
    return voltage_by_lat_lon

def get_voltage_dataframe(dss_instance: dss):
    """ Function to retrieve voltage dataframe for all buses. 
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect
    """

    all_bus_voltage = dss_instance.Circuit.AllBusMagPu()
    all_bus_names = dss_instance.Circuit.AllBusNames()

    voltage_df = {"busname": [], "voltage(pu)": []}

    for bus, voltage_pu in zip(all_bus_names, all_bus_voltage):
        voltage_df['busname'].append(bus)
        voltage_df['voltage(pu)'].append(voltage_pu)
    
    return pd.DataFrame(voltage_df).set_index("busname")



if __name__ == '__main__':

    pass
