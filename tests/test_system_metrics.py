""" This module contains tests for computing system level metrics."""
from pathlib import Path

from emerge.emerge.metrics import system_metrics
from emerge.emerge.metrics import observer
from conftest import simulation_manager_setup

# def test_total_energy():
#     """ Function to test the computation of total energy."""

#     manager = simulation_manager_setup()
#     subject = observer.MetricsSubject()

#     total_energy_observer = system_metrics.TotalEnergy()
#     subject.attach(total_energy_observer)

#     manager.simulate(subject)

# def test_pv_energy():
#     """ Function to test the computation of total PV energy."""

#     manager = simulation_manager_setup()
#     subject = observer.MetricsSubject()

#     pv_observer = system_metrics.TotalPVGeneration()
#     subject.attach(pv_observer)

#     manager.simulate(subject)

def test_energy_loss():
    """ Function to test the computation of total loss."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    loss_observer = system_metrics.TotalLossEnergy()
    subject.attach(loss_observer)

    manager.simulate(subject)
    print(loss_observer.get_metric())

def test_timeseries_powerloss():
    """ Function to test the computation of timeseries power loss."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    loss_observer = system_metrics.TimeseriesTotalLoss()
    subject.attach(loss_observer)

    manager.simulate(subject)
    print(loss_observer.get_metric())

# def test_sardi_voltage():
#     """ Function to test the computation of SARDI voltage."""

#     manager = simulation_manager_setup()
#     subject = observer.MetricsSubject()

#     sardi_voltage_observer = system_metrics.SARDI_voltage()
#     subject.attach(sardi_voltage_observer)

#     manager.simulate(subject)

# def test_sardi_line():
#     """ Function to test the computation of SARDI line."""

#     manager = simulation_manager_setup()
#     subject = observer.MetricsSubject()

#     sardi_line_observer = system_metrics.SARDI_line()
#     subject.attach(sardi_line_observer)

#     manager.simulate(subject)

# def test_sardi_transformer():
#     """ Function to test the computation of SARDI transformer."""

#     manager = simulation_manager_setup()
#     subject = observer.MetricsSubject()

#     sardi_xfmr_observer = system_metrics.SARDI_transformer()
#     subject.attach(sardi_xfmr_observer)

#     manager.simulate(subject)
#     print(sardi_xfmr_observer.get_metric())

# def test_sardi_aggregated():
#     """ Function to test the computation of SARDI aggregated."""

#     manager = simulation_manager_setup()
#     subject = observer.MetricsSubject()

#     sardi_aggregated_observer = system_metrics.SARDI_aggregated()
#     subject.attach(sardi_aggregated_observer)

#     manager.simulate(subject)


# def test_sardi_metrics():
#     """ Function for testing SARDI metrics. """

#     manager = simulation_manager_setup()
#     pvsystem_file = Path(__file__).absolute().parents[1]/ 'examples' / 'opendss' / 'PVSystems.dss'
#     manager.opendss_instance.execute_dss_command(f"redirect {pvsystem_file}")
#     subject = observer.MetricsSubject()
#     sardi_voltage_observer = system_metrics.SARDI_voltage()
#     sardi_line_observer = system_metrics.SARDI_line()
#     sardi_aggregated_observer = system_metrics.SARDI_aggregated()
#     sardi_xfmr_observer = system_metrics.SARDI_transformer()
    
#     subject.attach(sardi_voltage_observer)
#     subject.attach(sardi_line_observer)
#     subject.attach(sardi_xfmr_observer)
#     subject.attach(sardi_aggregated_observer)

#     manager.simulate(subject)

#     sardi_voltage = list(sardi_voltage_observer.get_metric().values())[0]
#     sardi_line = list(sardi_line_observer.get_metric().values())[0]
#     sardi_xfmr = list(sardi_xfmr_observer.get_metric().values())[0]
#     sardi_aggregated = list(sardi_aggregated_observer.get_metric().values())[0]

#     assert sardi_aggregated >= sardi_voltage
#     assert sardi_aggregated >= sardi_line
#     assert sardi_aggregated >= sardi_xfmr
