"""Extract base level metrics"""
from functools import cache

import numpy as np
import opendssdirect as odd
import pandas as pd
import polars as pl

from emerge.network.asset_metrics import networkx_from_opendss_model


def get_allbus_voltage_pu():
    return odd.Circuit.AllBusMagPu()


def get_voltage_distribution(
    voltage_array: list, bins: list = [0.7 + i * 0.05 for i in range(12)]
):
    voltage_array = np.array(voltage_array)
    voltage_array = voltage_array[voltage_array != 0]

    hist, _ = np.histogram(voltage_array, bins)
    pct_hist = list(np.array(hist) * 100 / len(voltage_array))

    return {"Voltage bins": bins[:-1], "Percentage nodes": pct_hist}


def get_voltage_by_distance():
    mapper = {1: "Phase A", 2: "Phase B", 3: "Phase C"}
    voltage_by_distance = {"Voltage (pu)": [], "Distance from substation (km)": [], "Phase": []}
    for phase in range(1, 4):
        pu_voltages = odd.Circuit.AllNodeVmagPUByPhase(phase)
        node_distances = odd.Circuit.AllNodeDistancesByPhase(phase)

        voltage_by_distance["Voltage (pu)"].extend(pu_voltages)
        voltage_by_distance["Phase"].extend([mapper[phase]] * len(pu_voltages))
        voltage_by_distance["Distance from substation (km)"].extend(node_distances)

    return voltage_by_distance


def get_voltage_by_lat_lon():
    network = networkx_from_opendss_model()
    node_data = {node[0]: node[1] for node in network.nodes.data()}
    all_bus_voltage = odd.Circuit.AllBusMagPu()
    all_bus_names = odd.Circuit.AllBusNames()

    voltage_by_lat_lon = {"longitudes": [], "latitudes": [], "voltage (pu)": []}

    for bus, voltage_pu in zip(all_bus_names, all_bus_voltage):
        voltage_by_lat_lon["latitudes"].append(node_data[bus]["pos"][1])
        voltage_by_lat_lon["longitudes"].append(node_data[bus]["pos"][0])
        voltage_by_lat_lon["voltage (pu)"].append(voltage_pu)

    return voltage_by_lat_lon


@cache
def get_buses() -> list[str]:
    """Returns list of buses for all nodes in current openodd circuit."""
    nodes = odd.Circuit.AllNodeNames()
    return [el.split(".")[0] for el in nodes]


@cache
def get_branch_elements() -> list[str]:
    """Returns list of buses for all branches in current openodd circuit."""
    return odd.PDElements.AllNames()


def get_voltage_dataframe():
    """Function to retrieve voltage dataframe for all buses."""
    voltage_df = {"busname": get_buses(), "voltage(pu)": odd.Circuit.AllBusMagPu()}
    return pl.DataFrame(voltage_df)


def get_loading_dataframe():
    """Function to retrieve line loading dataframe for all line segments."""
    loading = odd.PDElements.AllPctNorm(AllNodes=False)
    return pl.DataFrame({"branch": get_branch_elements(), "loading(pu)": np.array(loading) / 100})


def get_pv_power_dataframe():
    """Function to retrieve pv power dataframe."""
    pv_power_df = {"pvname": [], "active_power": [], "reactive_power": []}

    flag = odd.PVsystems.First()
    while flag > 0:
        pv_name = odd.PVsystems.Name().lower()
        pv_powers = odd.CktElement.Powers()

        active_power = -sum(pv_powers[::2])
        reactive_power = -sum(pv_powers[1::2])
        pv_power_df["pvname"].append(pv_name)
        pv_power_df["active_power"].append(active_power)
        pv_power_df["reactive_power"].append(reactive_power)

        flag = odd.PVsystems.Next()

    return pd.DataFrame(pv_power_df).set_index("pvname")
