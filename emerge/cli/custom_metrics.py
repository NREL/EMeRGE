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
                observers[key] = class_mapper[key](*subdict['args'])
    return observers

def _run_timeseries_sim(
        master_dss_file_path: str,
        start_time: str, 
        end_time: str, 
        profile_start_time: str,
        resolution_min: float,
        export_path: str,
        time_group: str,
        metrics,
        scenario_base_folder: str,
        pvshape = None,
        technologies = [],
        scenario_folder_path = None,
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

    if scenario_folder_path:

        if 'pvsystem' in technologies:
            pvsystem_file_path = scenario_folder_path / 'PVSystems.dss'
            manager.opendss_instance.execute_dss_command(f"Redirect {pvsystem_file_path}")
            manager.opendss_instance.execute_dss_command(f"batchedit pvsystem..* yearly={pvshape}")

    observers = _get_observers(metrics)
    for _, observer_ in observers.items():
        subject.attach(observer_)

    manager.simulate(subject)

    export_base_path = Path(export_path) / f"{scenario_base_folder}_{time_group}"
    if scenario_folder_path:
        export_base_path = export_base_path / scenario_folder_path.stem
    
    if not export_base_path.exists():
        export_base_path.mkdir(parents=True)
    
    manager.export_convergence(export_base_path / 'convergence_report.csv')
    observer.export_csv(list(observers.values()), export_base_path)

def _compute_scenario_custom_metrics(
    config, 
    technologies,
    master_dss_file,
    scenario_base_folder,
    scenario_folder_path=None, 
    pvshape=None,
):
    

    for time_group, time_dict in config['time_group'].items():
        _run_timeseries_sim(
            master_dss_file,
            time_dict['start_time'],
            time_dict['end_time'],
            config["profile_start"],
            config["resolution_min"],
            config["export_path"],
            time_group,
            config["metrics"],
            scenario_base_folder,
            pvshape,
            technologies,
            scenario_folder_path,
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


    if config.get('pv_scenarios', None):
       
        for folder_, master_file in config['pv_scenarios']['scenario_folder'].items():
            scen_folder = Path(config['pv_scenarios']['scenario_base_path']) / folder_
            if config['pv_scenarios']['num_core'] > 1:
                
                all_paths = list(scen_folder.iterdir())

                sim_inputs = list(zip(
                    [config]*len(all_paths),
                    [['pvsystem']]*len(all_paths),
                    [master_file]*len(all_paths),
                    [folder_]*len(all_paths),
                    all_paths,
                    [config['pv_scenarios']['pv_profile_shape']]*len(all_paths)
                ))

                with multiprocessing.Pool(config['pv_scenarios']['num_core']) as p:
                    p.starmap(_compute_scenario_custom_metrics, sim_inputs )
            else:
                for path in scen_folder.iterdir():
                    _compute_scenario_custom_metrics(
                        config,
                        ['pvsystem'],
                        master_dss_file,
                        folder_,
                        path,
                        config['pv_scenarios']['pv_profile_shape']  
                    )
    
    if config.get('base_scenarios', None):
        
        if config['base_scenarios']['num_core'] > 1:
            
            all_master_files = list(config['base_scenarios']['scenario_folder'].values())
            sim_inputs =  list(zip(
                    [config]*len(all_master_files),
                    [[]]*len(all_master_files),
                    all_master_files,
                    list(config['base_scenarios']['scenario_folder'].keys()),
                    [None]*len(all_master_files),
                    [None]*len(all_master_files)
                ))

            with multiprocessing.Pool(config['base_scenarios']['num_core']) as p:
                p.starmap(_compute_scenario_custom_metrics, sim_inputs)
        else:
            for key, path in config['base_scenarios']['scenario_folder'].items():
                _compute_scenario_custom_metrics(config, [], path, key, None, None )



    

    