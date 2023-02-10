""" Module for computing time series metrics for multi scenario simulation."""

import click
import datetime
import yaml
from pathlib import Path

from emerge.metrics.time_series_metrics import system_metrics
from emerge.metrics.time_series_metrics import observer
from emerge.metrics.time_series_metrics import simulation_manager
from emerge.metrics.time_series_metrics import node_voltage_stats
from emerge.metrics.time_series_metrics import line_loading_stats
from emerge.metrics.time_series_metrics import xfmr_loading_stats


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
    


    for _, observer_ in observers.items():
        subject.attach(observer_)

    manager.simulate(subject)

    export_base_path = Path(config['export_path'])
    if not export_base_path.exists():
        export_base_path.mkdir(parents=True)
    
    manager.export_convergence(export_base_path / 'convergence_report.csv')
    observer.export_csv(list(observers.values()), export_base_path)
    

    