""" Module for computing time series metrics for multi scenario simulation."""
# standard imports
import datetime
from pathlib import Path
import multiprocessing

# third-party imports
import click

# internal imports
from emerge.metrics import system_metrics
from emerge.metrics import observer
from emerge.metrics import node_metrics
from emerge.simulator import simulation_manager


def _run_timeseries_sim(input):

    date_format = "%Y-%m-%d %H:%M:%S"
    manager = simulation_manager.OpenDSSSimulationManager(
        input["master_file"],
        datetime.datetime.strptime(input["simulation_start"], date_format),
        datetime.datetime.strptime(input["profile_start"], date_format),
        datetime.datetime.strptime(input["simulation_end"], date_format),
        input["simulation_resolution"],
    )
    manager.opendss_instance.execute_dss_command(f"Redirect {input['pv_file']}")
    manager.opendss_instance.set_max_iteration(200)
    subject = observer.MetricsSubject()

    sardi_voltage_observer = system_metrics.SARDI_voltage(
        input["overvoltage_threshold"], input["undervoltage_threshold"]
    )
    sardi_line_observer = system_metrics.SARDI_line(input["thermal_threshold"])
    sardi_xfmr_observer = system_metrics.SARDI_transformer(
        input["thermal_threshold"]
    )
    sardi_aggregated_observer = system_metrics.SARDI_aggregated(
        loading_limit=input["thermal_threshold"],
        voltage_limit={
            "overvoltage_threshold": input["overvoltage_threshold"],
            "undervoltage_threshold": input["undervoltage_threshold"],
        },
    )
    nvri_observer = node_metrics.NVRI(
        input["overvoltage_threshold"], input["undervoltage_threshold"]
    )
    llri_observer = node_metrics.LLRI(input["thermal_threshold"])
    tlri_observer = node_metrics.TLRI(input["thermal_threshold"])
    total_energy_observer = system_metrics.TotalEnergy()
    total_pv_energy_observer = system_metrics.TotalPVGeneration()
    timeseries_total_power_observer = system_metrics.TimeseriesTotalPower()
    timeseries_total_pv_power_observer = system_metrics.TimeseriesTotalPVPower()
    total_loss_observer = system_metrics.TotalLossEnergy()
    timeseries_loss_observer = system_metrics.TimeseriesTotalLoss()

    observers_ = [
        sardi_voltage_observer,
        sardi_line_observer,
        sardi_xfmr_observer,
        sardi_aggregated_observer,
        nvri_observer,
        llri_observer,
        tlri_observer,
        total_energy_observer,
        total_pv_energy_observer,
        timeseries_total_power_observer,
        timeseries_total_pv_power_observer,
        total_loss_observer,
        timeseries_loss_observer
    ]
    for observer_ in observers_:
        subject.attach(observer_)

    manager.opendss_instance.execute_dss_command(f"batchedit pvsystem..* yearly={input['solar_profile']}")

    if input['voltvar']:
        num_points = len(input['voltvar_yarray'].split(','))
        curve_command = f"new xycurve.vvar_curve npts={num_points} yarray={input['voltvar_yarray']} xarray={input['voltvar_xarray']}"
        manager.opendss_instance.execute_dss_command(curve_command)
        
        inverter_command = f"new invcontrol.inv_controller_ mode=VOLTVAR voltage_curvex_ref=rated vvc_curve1=vvar_curve eventlog=yes RefReactivePower=VARMAX_VARS"
        manager.opendss_instance.execute_dss_command(inverter_command)

        manager.opendss_instance.execute_dss_command("batchedit pvsystem..* wattpriority=yes")
        if not input['nighttime']:
            manager.opendss_instance.execute_dss_command("batchedit pvsystem..* varfollowinverter=yes")

    manager.simulate(subject)
    manager.export_convergence(input["convergence_report"])
    observer.export_tinydb_json(observers_, input["output_json"])


@click.command()
@click.option(
    "-m",
    "--master-file",
    help="Path to master dss file",
)
@click.option(
    "-sf",
    "--scenario-folder",
    help="Path to a scenario folder",
)
@click.option(
    "-pn",
    "--profile-name",
    help="Profile name for solar.",
)
@click.option(
    "-nc",
    "--number-of-cores",
    default=1,
    show_default=True,
    help="Number of cores to be used in parallel",
)
@click.option(
    "-ss",
    "--simulation-start",
    default="2022-1-1 00:00:00",
    show_default=True,
    help="Simulation start time.",
)
@click.option(
    "-ps",
    "--profile-start",
    default="2022-1-1 00:00:00",
    show_default=True,
    help="Time series profile start time.",
)
@click.option(
    "-se",
    "--simulation-end",
    default="2022-1-2 00:00:00",
    show_default=True,
    help="Simulation end time.",
)
@click.option(
    "-r",
    "--simulation-resolution",
    default=60,
    show_default=True,
    help="Simulation time resolution in minutes.",
)
@click.option(
    "-ot",
    "--overvoltage-threshold",
    default=1.05,
    show_default=True,
    help="Overvoltage threshold.",
)
@click.option(
    "-ut",
    "--undervoltage-threshold",
    default=0.95,
    show_default=True,
    help="Undervoltage threshold.",
)
@click.option(
    "-tt",
    "--thermal-threshold",
    default=0.95,
    show_default=True,
    help="Thermal laoding threshold.",
)
@click.option(
    "-vvar",
    "--voltvar",
    default=False,
    show_default=True,
    help="Voltvar smart inverter settings."
)
@click.option(
    "-qx",
    "--voltvar-xarray",
    default="[0.7,0.92,0.967,1.033,1.07,1.3]",
    show_default=True,
    help="X array for voltvar curve"
)
@click.option(
    "-qy",
    "--voltvar-yarray",
    default="[0.44,0.44,0,0,-0.44, -0.44]",
    show_default=True,
    help="Y array for voltvar curve"
)
@click.option(
    "-nt",
    "--nighttime",
    default=True,
    show_default=True,
    help="Inverter night time volt var setting."
)
@click.option(
    "-o",
    "--output-folder",
    help="Path to a scenario folder",
)
def compute_multiscenario_time_series_metrics(
    master_file,
    scenario_folder,
    profile_name,
    number_of_cores,
    simulation_start,
    profile_start,
    simulation_end,
    simulation_resolution,
    overvoltage_threshold,
    undervoltage_threshold,
    thermal_threshold,
    voltvar,
    voltvar_xarray,
    voltvar_yarray,
    nighttime,
    output_folder,
):
    """Run multiscenario time series simulation and compute
    time series metrics."""

    scenario_folder = Path(scenario_folder)
    output_folder = Path(output_folder)

    output_folder.mkdir(exist_ok=True)

    timeseries_input = []

    for folder_path in scenario_folder.iterdir():
        pvsystem_file = folder_path / "PVSystems.dss"
        json_path = output_folder / (folder_path.name + ".json")
        convergence_file = output_folder / (folder_path.name + "_convergence.csv")
        timeseries_input.append(
            {
                "master_file": master_file,
                "simulation_start": simulation_start,
                "solar_profile": profile_name,
                "profile_start": profile_start,
                "simulation_end": simulation_end,
                "simulation_resolution": simulation_resolution,
                "pv_file": pvsystem_file,
                "overvoltage_threshold": overvoltage_threshold,
                "undervoltage_threshold": undervoltage_threshold,
                "thermal_threshold": thermal_threshold,
                "output_json": json_path,
                "convergence_report": convergence_file,
                "voltvar": voltvar,
                "nighttime": nighttime,
                "voltvar_xarray": voltvar_xarray,
                "voltvar_yarray": voltvar_yarray
            }
        )

    with multiprocessing.Pool(number_of_cores) as p:
        p.map(_run_timeseries_sim, timeseries_input)
