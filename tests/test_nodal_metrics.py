""" This module contains tests for computing system level metrics."""

from emerge.metrics import node_metrics
from emerge.metrics import observer
from conftest import simulation_manager_setup

def test_nvri_metric():
    """ Function to test the computation of NVRI ."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    nvri_observer = node_metrics.NVRI()
    subject.attach(nvri_observer)

    manager.simulate(subject)
    nvri = nvri_observer.get_metric()
    assert nvri

def test_llri_metric():
    """ Function to test the computation of LLRI ."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    llri_observer = node_metrics.LLRI()
    subject.attach(llri_observer)

    manager.simulate(subject)
    llri = llri_observer.get_metric()
    assert llri

def test_tlri_metric():
    """ Function to test the computation of TLRI ."""

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    tlri_observer = node_metrics.TLRI()
    subject.attach(tlri_observer)

    manager.simulate(subject)
    tlri = tlri_observer.get_metric()
    assert tlri
