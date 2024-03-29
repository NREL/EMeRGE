"""
Higher level wrapper to compute all the metrics
"""

# third-party imports
from pathlib import Path

# internal imports
from emerge.utils.util import setup_logging
from emerge.db.db_handler import TinyDBHandler
from emerge.simulator.opendss import OpenDSSSimulator
from emerge.network.asset_metrics import (aggregate_asset_metrics,
    get_coordinates)
from emerge.simulator.powerflow_results import (
    get_allbus_voltage_pu,
    get_voltage_by_distance,
    get_voltage_by_lat_lon,
    get_voltage_distribution,
    get_lineloading_dataframe,
    get_transloading_dataframe
)

def compute_snapshot_metrics(
    master_dss_file_path: str,
    output_path: str = Path(__file__).parents[2] / 'db.json'
):
    """ Computes metrics for snapshot powerflow results. It takes master dss file and
    computes all the snapshot metrics for the purpose of visualization. This will create a
    db json file which is used by dashboard to plot results """
    
    setup_logging()
    db_instance = TinyDBHandler(output_path)
    opendss_instance = OpenDSSSimulator(master_dss_file_path)
    opendss_instance.solve()
    
    """ Get all the asset metrics """
    asset_metrics = aggregate_asset_metrics(opendss_instance.dss_instance).dict()
    db_instance.db.insert({"type": "asset_metrics", "metrics": asset_metrics})
    
    """ Get coordinates """
    coordinates = get_coordinates(opendss_instance.dss_instance)
    db_instance.db.insert({"type": "coordinates", "data": coordinates})

    """ Get voltage pu distributions """
    voltages = get_allbus_voltage_pu(opendss_instance.dss_instance)
    voltage_bins = get_voltage_distribution(voltages)
    db_instance.db.insert({"type": "snapshot_voltage_bins", \
        "label": "peak_load", "data": voltage_bins })

    """ Get voltage pu by disyance"""
    voltage_by_distance = get_voltage_by_distance(opendss_instance.dss_instance)
    db_instance.db.insert({"type": "snapshot_voltage_by_distance", \
        "label": "peak_load", "data":  voltage_by_distance})

    """ Get voltage by lat lons"""
    voltage_by_lat_lon = get_voltage_by_lat_lon(opendss_instance.dss_instance)
    db_instance.db.insert({
            "type": "snapshot_voltage_for_heatmap", 
            "label": "peak_load", 
            "data":  voltage_by_lat_lon})

    """ line loading """
    line_loading_df = get_lineloading_dataframe(opendss_instance.dss_instance)
    db_instance.db.insert({
            "type": "snapshot_lineloading_for_heatmap", 
            "label": "peak_load", 
            "data":  line_loading_df.to_dict()['loading(pu)']})

    """ transformer loading """
    xfmr_loading_df = get_transloading_dataframe(opendss_instance.dss_instance)
    db_instance.db.insert({
            "type": "snapshot_xfmrloading_for_heatmap", 
            "label": "peak_load", 
            "data":  xfmr_loading_df.to_dict()['loading(pu)']})

