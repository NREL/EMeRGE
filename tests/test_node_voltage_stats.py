""" This module contains tests for computing system level metrics."""

from emerge.metrics.time_series_metrics import node_voltage_stats
from emerge.metrics.time_series_metrics import observer
from conftest import simulation_manager_setup

def test_node_voltage_stats_metric():
    """ Function to test the computation of Node voltage statistical metrics."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    node_v_obs = node_voltage_stats.NodeVoltageStats()
    subject.attach(node_v_obs)

    manager.simulate(subject)
    node_v = node_v_obs.get_metric()
    print(node_v)


def test_node_voltage_bins():
    """ Function to test the computation of Node voltage bins."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    node_v_obs = node_voltage_stats.NodeVoltageBins(
        [0.95, 0.98, 1.02, 1.05]
    )
    subject.attach(node_v_obs)

    manager.simulate(subject)
    node_v = node_v_obs.get_metric()
    print(node_v)