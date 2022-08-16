""" This module contains tests for computing system level metrics."""

from emerge.metrics.time_series_metrics import system_metrics
from emerge.metrics.time_series_metrics import observer
from emerge.metrics.time_series_metrics import system_metrics
from conftest import simulation_manager_setup

def test_sardi_voltage():
    """ Function to test the computation of SARDI voltage."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    sardi_voltage_observer = system_metrics.SARDI_voltage()
    subject.attach(sardi_voltage_observer)

    manager.simulate(subject)
    print(sardi_voltage_observer.get_metric())

