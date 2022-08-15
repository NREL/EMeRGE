""" Module for testing opendss time series simulation. """

from pathlib import Path
import datetime

from emerge.metrics.time_series_metrics import simulation_manager

def test_timeseries_simulation():
    """ Function for tesitng basic time series simulation capability"""

    root_path = Path(__file__).absolute().parents[1] 
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'
    manager = simulation_manager.OpenDSSSimulationManager(
        str(master_dss_file),
        datetime.datetime(2022, 1,1, 0, 0,0),
        datetime.datetime(2022,1,1,0,0,0),
        datetime.datetime(2022,1,2,0,0,0),
        60
    )
    manager.simulate()
    manager.export_convergence()

    convergence_file = Path('convergence.csv')
    assert convergence_file.exists()
    convergence_file.unlink()