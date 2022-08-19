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

def test_sardi_line():
    """ Function to test the computation of SARDI line."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    sardi_line_observer = system_metrics.SARDI_line()
    subject.attach(sardi_line_observer)

    manager.simulate(subject)

def test_sardi_transformer():
    """ Function to test the computation of SARDI transformer."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    sardi_xfmr_observer = system_metrics.SARDI_transformer()
    subject.attach(sardi_xfmr_observer)

    manager.simulate(subject)
    print(sardi_xfmr_observer.get_metric())

def test_sardi_aggregated():
    """ Function to test the computation of SARDI aggregated."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    sardi_aggregated_observer = system_metrics.SARDI_aggregated()
    subject.attach(sardi_aggregated_observer)

    manager.simulate(subject)

