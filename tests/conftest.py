""" Module for managing pytest configuration. """

import datetime
from pathlib import Path

from emerge.simulator import simulation_manager, opendss

def simulation_manager_setup() -> simulation_manager.OpenDSSSimulationManager:
    """ Fixture function for setting up simulation manager. """
    root_path = Path(__file__).absolute().parents[1] 
    master_dss_file = root_path / 'examples' / 'opendss' / 'master.dss'
    manager = simulation_manager.OpenDSSSimulationManager(
        opendss.OpenDSSSimulator(master_dss_file),
        datetime.datetime(2022,1,1,0,0,0),
        datetime.datetime(2022,1,1,0,0,0),
        datetime.datetime(2022,1,2,0,0,0),
        60
    )

    return manager