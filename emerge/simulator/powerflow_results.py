

"""
 Extract base level metrics
"""
# standard imports
import math

# third-party imports
import numpy as np
import opendssdirect as dss
import pandas as pd

# internal imports
from emerge.network.asset_metrics import networkx_from_opendss_model


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


def get_lineloading_dataframe(dss_instance: dss):
    """ Function to retrieve line loading dataframe for all line segments. 
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect
    """
    line_loading_df = {"linename": [], "loading(pu)": []}

    dss_instance.Circuit.SetActiveClass("Line")
    flag = dss_instance.ActiveClass.First()

    while flag:
        line_name = dss_instance.CktElement.Name().lower()
        n_phases = dss_instance.CktElement.NumPhases()
        line_limit = dss_instance.CktElement.NormalAmps()
        currents = dss_instance.CktElement.CurrentsMagAng()[:2 * n_phases]
        line_current = currents[::2]
        ldg = max(line_current) / max(float(line_limit), 1)
        line_loading_df['linename'].append(line_name)
        line_loading_df['loading(pu)'].append(ldg)
        flag = dss_instance.ActiveClass.Next()
    
    return pd.DataFrame(line_loading_df).set_index("linename")

def get_pv_power_dataframe(dss_instance: dss):
    """ Function to retrieve pv power dataframe.
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect
    """
    pv_power_df = {"pvname": [], "active_power": [], "reactive_power": []}

    flag = dss_instance.PVsystems.First()
    while flag>0:
        pv_name = dss_instance.PVsystems.Name().lower()
        pv_powers = dss_instance.CktElement.Powers()
        
        active_power = -sum(pv_powers[::2]) 
        reactive_power = -sum(pv_powers[1::2]) 
        pv_power_df['pvname'].append(pv_name)
        pv_power_df['active_power'].append(active_power)
        pv_power_df['reactive_power'].append(reactive_power)
        
        flag = dss_instance.PVsystems.Next()
    
    return pd.DataFrame(pv_power_df).set_index("pvname")



def get_transloading_dataframe(dss_instance: dss):
    """ Function to retrieve transformer loading dataframe for all transformers. 
    
    Args:
        dss_instance (dss): Instance of OpenDSSDirect
    """
    trans_loading_df = {"transformername": [], "loading(pu)": []}

    dss_instance.Circuit.SetActiveClass("Transformer")
    flag = dss_instance.ActiveClass.First()

    while flag:
        xfmr_name = dss_instance.CktElement.Name().lower()
        n_phases = dss_instance.CktElement.NumPhases()
        hs_kv = float(dss_instance.Properties.Value('kVs').split('[')[1].split(',')[0])
        kva = float(dss_instance.Properties.Value('kVA'))
        if n_phases > 1:
            xfmr_limit = kva / (hs_kv * math.sqrt(3))
        else:
            xfmr_limit = kva / (hs_kv)
        currents = dss_instance.CktElement.CurrentsMagAng()[:2 * n_phases]
        xfmr_current = currents[::2]
        ldg = max(xfmr_current) / float(xfmr_limit)
        
        trans_loading_df['transformername'].append(xfmr_name)
        trans_loading_df['loading(pu)'].append(ldg)
        flag = dss_instance.ActiveClass.Next()
    
    return pd.DataFrame(trans_loading_df).set_index("transformername")

