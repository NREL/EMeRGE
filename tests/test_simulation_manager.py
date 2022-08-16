""" Module for testing opendss time series simulation. """

from pathlib import Path

from conftest import simulation_manager_setup

def test_timeseries_simulation():
    """ Function for tesitng basic time series simulation capability"""

    manager = simulation_manager_setup()
    manager.simulate()
    manager.export_convergence()

    convergence_file = Path('convergence.csv')
    assert convergence_file.exists()
    convergence_file.unlink()