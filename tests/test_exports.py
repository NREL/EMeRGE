""" Modules containing test for exporting metrics. """


from emerge.metrics.time_series_metrics import system_metrics
from emerge.metrics.time_series_metrics import observer
from emerge.metrics.time_series_metrics import node_metrics
from conftest import simulation_manager_setup

def test_export_metrics():
    """ Test exporting metrics. """

    manager = simulation_manager_setup()
    subject = observer.MetricsSubject()

    sardi_voltage_observer = system_metrics.SARDI_voltage()
    sardi_line_observer = system_metrics.SARDI_line()
    sardi_xfmr_observer = system_metrics.SARDI_transformer()
    sardi_aggregated_observer = system_metrics.SARDI_aggregated()
    nvri_observer = node_metrics.NVRI()
    llri_observer = node_metrics.LLRI()
    tlri_observer = node_metrics.TLRI()
    
    observers_ = [sardi_voltage_observer, sardi_line_observer,
        sardi_xfmr_observer, sardi_aggregated_observer, nvri_observer,
        llri_observer, tlri_observer]
    for observer_ in observers_:
        subject.attach(observer_)

    manager.simulate(subject)
    observer.export_tinydb_json(observers_, "db_metrics.json")