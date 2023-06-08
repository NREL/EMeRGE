""" Module for computing time series metrics for multi scenario simulation."""

import click
import datetime
import yaml
from pathlib import Path
import multiprocessing

from emerge.metrics.time_series_metrics import system_metrics
from emerge.metrics.time_series_metrics import observer
from emerge.metrics.time_series_metrics import simulation_manager
from emerge.metrics.time_series_metrics import node_voltage_stats
from emerge.metrics.time_series_metrics import line_loading_stats
from emerge.metrics.time_series_metrics import xfmr_loading_stats

def _compute_custom_metrics(config, pvsystem_folder_path=None):
    date_format = "%Y-%m-%d %H:%M:%S"
    manager = simulation_manager.OpenDSSSimulationManager(
        config["master"],
        datetime.datetime.strptime(config["start_time"], date_format),
        datetime.datetime.strptime(config["profile_start"], date_format),
        datetime.datetime.strptime(config["end_time"], date_format),
        config["resolution_min"],
    )
    manager.opendss_instance.set_max_iteration(200)
    subject = observer.MetricsSubject()

    if pvsystem_folder_path:
        pvsystem_file_path = pvsystem_folder_path / 'PVSystems.dss'
        manager.opendss_instance.execute_dss_command(f"Redirect {pvsystem_file_path}")
        manager.opendss_instance.execute_dss_command(f"batchedit pvsystem..* yearly={config['multi_scenario']['pv_profile_shape']}")


    observers = {}
    if 'substation_power' in config['metrics']:
        observers['substation_power'] = system_metrics.TimeseriesTotalPower()
    
    if 'total_powerloss' in config['metrics']:
        observers['total_powerloss'] = system_metrics.TimeseriesTotalLoss()
    
    if 'node_voltage_stats' in config['metrics']:
        observers['node_voltage_stats'] = node_voltage_stats.NodeVoltageStats()

    if 'node_voltage_bins' in config['metrics']:
        observers['node_voltage_bins'] = node_voltage_stats.NodeVoltageBins(
            config['metrics']['node_voltage_bins']['voltage_bins']
        )
    if 'line_loading_stats' in config['metrics']:
        observers['line_loading_stats'] = line_loading_stats.LineLoadingStats()

    if 'line_loading_bins' in config['metrics']:
        observers['line_loading_bins'] = line_loading_stats.LineLoadingBins(
            config['metrics']['line_loading_bins']['loading_bins']
        )

    if 'xfmr_loading_stats' in config['metrics']:
        observers['xfmr_loading_stats'] = xfmr_loading_stats.XfmrLoadingStats()

    if 'xfmr_loading_bins' in config['metrics']:
        observers['xfmr_loading_bins'] = xfmr_loading_stats.XfmrLoadingBins(
            config['metrics']['xfmr_loading_bins']['loading_bins']
        )
    if 'overloaded_lines' in config['metrics']:
        observers['overloaded_lines'] = line_loading_stats.OverloadedLines()

    if 'overloaded_transformers' in config['metrics']:
        observers['overloaded_transformers'] = xfmr_loading_stats.OverloadedTransformers()

    if 'sardi_voltage' in config['metrics']:
        observers['sardi_voltage'] = system_metrics.SARDI_voltage(
            config['metrics']['sardi_voltage']["ov_threshold"], 
            config['metrics']['sardi_voltage']['uv_threshold']
        )
    
    if 'sardi_line' in config['metrics']:
        observers['sardi_line'] = system_metrics.SARDI_line(
            config['metrics']['sardi_line']["thermal_threshold"])
    if 'sardi_xfmr' in config['metrics']:
        observers['sardi_xfmr'] = system_metrics.SARDI_transformer(
             config['metrics']['sardi_xfmr']["thermal_threshold"]
        )
    if 'sardi_aggregated' in config['metrics']:
        observers['sardi_aggregated'] = system_metrics.SARDI_aggregated(
            loading_limit= config['metrics']['sardi_aggregated']["thermal_threshold"],
            voltage_limit={
                "overvoltage_threshold": config['metrics']['sardi_aggregated']["ov_threshold"],
                "undervoltage_threshold": config['metrics']['sardi_aggregated']["uv_threshold"],
            },
        )

    for _, observer_ in observers.items():
        subject.attach(observer_)

    manager.simulate(subject)

    export_base_path = Path(config['export_path']) if not pvsystem_folder_path else \
        Path(config['export_path']) / pvsystem_file_path.parent.name
    
    if not export_base_path.exists():
        export_base_path.mkdir(parents=True)
    
    manager.export_convergence(export_base_path / 'convergence_report.csv')
    observer.export_csv(list(observers.values()), export_base_path)


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
        if config['multi_scenario']['num_core'] > 1:
            all_paths = list(scen_folder.iterdir())
            with multiprocessing.Pool(config['multi_scenario']['num_core']) as p:
                p.starmap(_compute_custom_metrics, list(zip([config]*len(all_paths), all_paths)))
        else:
            for path in scen_folder.iterdir():
                _compute_custom_metrics(config, path)
    else:
        _compute_custom_metrics(config)

    

    