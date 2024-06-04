""" Module for computing time series metrics for multi scenario simulation."""

import datetime
from pathlib import Path
from typing import Dict
import concurrent.futures

import click
from emerge.simulator.opendss import OpenDSSSimulator
import yaml

from emerge.metrics import system_metrics
from emerge.metrics import observer
from emerge.simulator import simulation_manager
from emerge.metrics import node_voltage_stats
from emerge.metrics import line_loading_stats


def get_observers(metrics: Dict):
    observers = {}

    class_mapper = {
        'substation_power': system_metrics.TimeseriesTotalPower,
        'total_pvpower': system_metrics.TimeseriesTotalPVPower,
        'total_powerloss': system_metrics.TimeseriesTotalLoss,
        'node_voltage_stats': node_voltage_stats.NodeVoltageStats,
        'node_voltage_bins': node_voltage_stats.NodeVoltageBins,
        'line_loading_stats': line_loading_stats.LineLoadingStats,
        'line_loading_bins': line_loading_stats.LineLoadingBins,
        'overloaded_lines': line_loading_stats.OverloadedLines,
        'sardi_voltage': system_metrics.SARDI_voltage,
        'sardi_line': system_metrics.SARDI_line,
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
        scenario_folder_path = None,
):
    date_format = "%Y-%m-%d %H:%M:%S"
    opendss_instance = OpenDSSSimulator(master_dss_file_path)
    manager = simulation_manager.OpenDSSSimulationManager(
                opendss_instance,
                datetime.datetime.strptime(start_time, date_format),
                datetime.datetime.strptime(profile_start_time, date_format),
                datetime.datetime.strptime(end_time, date_format),
                resolution_min,
            )
    manager.opendss_instance.set_max_iteration(200)
    subject = observer.MetricsSubject() 

    if scenario_folder_path:

        for file_path in scenario_folder_path.iterdir():
            manager.opendss_instance.execute_dss_command(f"Redirect {file_path}")


    observers = get_observers(metrics)
    for _, observer_ in observers.items():
        subject.attach(observer_)

    manager.simulate(subject)

    export_base_path = Path(export_path) / f"{scenario_base_folder}_{time_group}"
    
    if scenario_folder_path:
        export_base_path = export_base_path / scenario_folder_path.name
    
    if not export_base_path.exists():
        export_base_path.mkdir(parents=True)
    
    manager.export_convergence(export_base_path / 'convergence_report.csv')
    observer.export_csv(list(observers.values()), export_base_path)


def _compute_scenario_custom_metrics_wrapper(input):
    _compute_scenario_custom_metrics(*input)

def _compute_scenario_custom_metrics(
    config, 
    master_dss_file,
    scenario_base_folder,
    scenario_folder_path=None, 
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
                    [master_file]*len(all_paths),
                    [folder_]*len(all_paths),
                    all_paths
                ))
                with concurrent.futures.ProcessPoolExecutor(
                    max_workers=config['pv_scenarios']['num_core']) as executor:
                    for input, _ in zip(sim_inputs, 
                                        executor.map(_compute_scenario_custom_metrics_wrapper, 
                                        sim_inputs)):
                        print(f'{input} completed ...')
                # with multiprocessing.Pool(config['pv_scenarios']['num_core']) as p:
                #     _ = p.starmap(_compute_scenario_custom_metrics, sim_inputs )
            else:
                for path in scen_folder.iterdir():
                    _compute_scenario_custom_metrics(
                        config,
                        master_file,
                        folder_,
                        path  
                    )
    
    if config.get('base_scenarios', None):
        
        if config['base_scenarios']['num_core'] > 1:
            
            all_master_files = list(config['base_scenarios']['scenario_folder'].values())
            sim_inputs =  list(zip(
                    [config]*len(all_master_files),
                    all_master_files,
                    list(config['base_scenarios']['scenario_folder'].keys()),
                    [None]*len(all_master_files),
                ))
            
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=config['base_scenarios']['num_core']) as executor:
                for input, _ in zip(sim_inputs, executor.map(
                        _compute_scenario_custom_metrics_wrapper, 
                        sim_inputs)):
                    print(f'{input} completed ...')

            # with multiprocessing.Pool(config['base_scenarios']['num_core']) as p:
            #     _ = p.starmap(_compute_scenario_custom_metrics, sim_inputs)
        else:
            for key, path in config['base_scenarios']['scenario_folder'].items():
                _compute_scenario_custom_metrics(config, [], path, key, None, None )



    

    