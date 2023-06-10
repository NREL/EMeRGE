""" Module for computing time series metrics for multi scenario simulation."""

import click
import datetime
import yaml
from pathlib import Path
import multiprocessing
from typing import Dict

from emerge.metrics.time_series_metrics import system_metrics
from emerge.metrics.time_series_metrics import observer
from emerge.metrics.time_series_metrics import simulation_manager
from emerge.metrics.time_series_metrics import node_voltage_stats
from emerge.metrics.time_series_metrics import line_loading_stats
from emerge.metrics.time_series_metrics import xfmr_loading_stats


def _get_observers(metrics: Dict):
    observers = {}

    class_mapper = {
        'substation_power': system_metrics.TimeseriesTotalPower,
        'total_pvpower': system_metrics.TimeseriesTotalPVPower,
        'total_powerloss': system_metrics.TimeseriesTotalLoss,
        'node_voltage_stats': node_voltage_stats.NodeVoltageStats,
        'node_voltage_bins': node_voltage_stats.NodeVoltageBins,
        'line_loading_stats': line_loading_stats.LineLoadingStats,
        'line_loading_bins': line_loading_stats.LineLoadingBins,
        'xfmr_loading_stats': xfmr_loading_stats.XfmrLoadingStats,
        'xfmr_loading_bins': xfmr_loading_stats.XfmrLoadingBins,
        'overloaded_lines': line_loading_stats.OverloadedLines,
        'overloaded_transformers': xfmr_loading_stats.OverloadedTransformers,
        'sardi_voltage': system_metrics.SARDI_voltage,
        'sardi_line': system_metrics.SARDI_line,
        'sardi_xfmr': system_metrics.SARDI_transformer,
        'sardi_aggregated': system_metrics.SARDI_aggregated
    }

    for key, subdict in metrics.items():
        if key in class_mapper:
            if 'args' not in subdict:
                observers[key] = class_mapper[key]()
            else:
                observers[key] = class_mapper[key](**subdict['args'])
    return observers

def _run_timeseries_sim(
        master_dss_file_path: str,
        start_time: str, 
        end_time: str, 
        profile_start_time: str,
        resolution_min: float,
        export_path: str,
        pvshape = None,
        pvsystem_folder_path = None,
        time_group = None,
        scenario_folder = None
):
    date_format = "%Y-%m-%d %H:%M:%S"
    manager = simulation_manager.OpenDSSSimulationManager(
                master_dss_file_path,
                datetime.datetime.strptime(start_time, date_format),
                datetime.datetime.strptime(profile_start_time, date_format),
                datetime.datetime.strptime(end_time, date_format),
                resolution_min,
            )
    manager.opendss_instance.set_max_iteration(200)
    subject = observer.MetricsSubject() 

    if pvsystem_folder_path:
        pvsystem_file_path = pvsystem_folder_path / 'PVSystems.dss'
        manager.opendss_instance.execute_dss_command(f"Redirect {pvsystem_file_path}")
        manager.opendss_instance.execute_dss_command(f"batchedit pvsystem..* yearly={pvshape}")

    observers = _get_observers()
    for _, observer_ in observers.items():
        subject.attach(observer_)

    manager.simulate(subject)

    export_base_path = Path(export_path) 
    if scenario_folder:
        if time_group:
            scenario_folder = f"{scenario_folder}_{time_group}"
        export_base_path = export_base_path / scenario_folder 
    
    if pvsystem_folder_path:
        export_base_path = export_base_path / pvsystem_file_path.parent.name
    
    if not export_base_path.exists():
        export_base_path.mkdir(parents=True)
    
    manager.export_convergence(export_base_path / 'convergence_report.csv')
    observer.export_csv(list(observers.values()), export_base_path)

def _compute_custom_metrics(config, pvsystem_folder_path=None, scenario_folder=None):
    

    if config['multi_time']:
        for time_group, time_dict in config['multi_time'].items():
            _run_timeseries_sim(
                config["master"],
                time_dict['start_time'],
                time_dict['end_time'],
                config["profile_start"],
                config["resolution_min"],
                config["export_path"],
                config['multi_scenario']['pv_profile_shape'],
                pvsystem_folder_path,
                time_group,
                scenario_folder
            )
    else:
        _run_timeseries_sim(
                config["master"],
                config['start_time'],
                config['end_time'],
                config["profile_start"],
                config["resolution_min"],
                config["export_path"],
                config['multi_scenario']['pv_profile_shape'],
                pvsystem_folder_path,
                None,
                scenario_folder
            )
            

@click.command()
@click.option(
    "-c",
    "--config-file",
    help="Path to config yaml file.",
)
def compute_custom_metrics(
    config_file
):
    """Compute custom metrics after running time series powerflow."""

    with open(config_file, "r") as fp:
        config = yaml.safe_load(fp)


    if config.get('multi_scenario', None):

        scen_folder = Path(config['multi_scenario']['scenario_folder'])
        for folder_ in scen_folder.iterdir():
            if config['multi_scenario']['num_core'] > 1:
                all_paths = list(folder_.iterdir())
                with multiprocessing.Pool(config['multi_scenario']['num_core']) as p:
                    p.starmap(_compute_custom_metrics, list(zip([config]*len(all_paths), all_paths, folder_)))
            else:
                for path in scen_folder.iterdir():
                    _compute_custom_metrics(config, path, folder_)
    else:
        _compute_custom_metrics(config)

    

    