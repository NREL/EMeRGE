""" This module manages time series simulation for computing 
time series metrics. """

from typing import Union
import datetime
import logging

import pandas as pd

from emerge.simulator import opendss
from emerge.metrics.time_series_metrics import observer


logger = logging.getLogger(__name__)
logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.DEBUG)

class OpenDSSSimulationManager:
    """ Class for managing time series simulation using OpenDSS.
    
    Attributes:
        path_to_master_dss_file (str): Path to Master.dss file
        simulation_start_time (datetime.datetime): Datetime indicating
            simulation start time
        profile_start_time (datetime.datetime): Datetime indicating
            profile start time
        simulation_end_time (datetime.datetime): Datetime indicating
            when the simulation finishes
        simulation_timestep_min (float): Simulation time resolution
            in minutes
    """

    def __init__(
        self,
        path_to_master_dss_file: str,
        simulation_start_time: datetime.datetime,
        profile_start_time: datetime.datetime,
        simulation_end_time: datetime.datetime,
        simulation_timestep_min: float,
    )-> None:
        
        self.path_to_master_dss_file = path_to_master_dss_file
        self.simulation_start_time = simulation_start_time
        self.profile_start_time = profile_start_time
        self.simulation_end_time = simulation_end_time
        self.simulation_timestep_min = simulation_timestep_min

        self.opendss_instance = opendss.OpenDSSSimulator(self.path_to_master_dss_file)
        self.opendss_instance.set_mode(2)
        self.opendss_instance.set_simulation_time(
            self.simulation_start_time,
            self.profile_start_time
        )
        self.opendss_instance.set_stepsize(self.simulation_timestep_min)
        self.opendss_instance.set_max_iteration(1000)
        self.current_time = self.simulation_start_time
        self.convergence_dict  = {"datetime": [], "convergence": []}


    def update_convergence_dict(self, current_time: datetime.datetime, convergence:bool):
        """ Updates convergence dict. """
        self.convergence_dict['datetime'].append(current_time)
        self.convergence_dict['convergence'].append(convergence)

    def export_convergence(self, export_path:str = './convergence.csv'):
        """ Export the convergence."""
        
        export_df = pd.DataFrame(self.convergence_dict)
        export_df.to_csv(export_path)


    def simulate(self, subject: Union[observer.MetricsSubject, None] = None):
        """ Loops through all the simulation timesteps """

        while self.current_time <= self.simulation_end_time:
            
            convergence = self.opendss_instance.solve()
            self.update_convergence_dict(self.current_time, convergence)

            if subject:
                subject.notify(self.opendss_instance.dss_instance)
            
            self.current_time += datetime.timedelta(minutes=self.simulation_timestep_min)
            logger.info(f"Simulation finished for {self.current_time} >> {convergence}")


    

        



