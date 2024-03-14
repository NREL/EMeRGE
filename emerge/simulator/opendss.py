""" OpenDSS simulator service for performing power flow."""

# standard imports
from pathlib import Path
import logging
from abc import ABC, abstractmethod

# third-party imports
import opendssdirect as dss

# internal imports
from emerge.utils.util import validate_path

logger = logging.getLogger(__name__)


class AbstractSimulator(ABC):

    @abstractmethod
    def set_stepsize(self, step_in_min):
        pass

    @abstractmethod
    def solve(self):
        pass

    @abstractmethod
    def set_simulation_time(self, sim_time, profile_start_time):
        pass 


class OpenDSSSimulator(AbstractSimulator):

    def __init__(self, 
            path_to_master_dss_file,
        ):

        validate_path(path_to_master_dss_file, check_for_dir=False, \
            check_for_file=True, file_types=['.dss'])
        
        self.case_file = Path(path_to_master_dss_file)
        self.dss_instance = dss

        self.dss_instance.run_command("Clear")
        self.dss_instance.Basic.ClearAll()
        self.execute_dss_command(f'Redirect {self.case_file}')

    def execute_dss_command(self, dss_command: str):
        
        error = self.dss_instance.run_command(dss_command)
        if error:
            logger.error(f"Error executing command {dss_command} >> {error}")
            raise Exception(f"Error executing command {dss_command} >> {error}")
        logger.info(f"Sucessfully executed the command, {dss_command}")
        return error

    def set_frequency(self, frequency):
        self.execute_dss_command(f"Set DefaultBaseFrequency={frequency}")
        

    def set_mode(self, mode):
        ## Use it wisely if you need to e.g. mode =2 means QSTS powerflow
        self.dss_instance.Solution.Mode(mode)

    def set_max_iteration(self, max_iterations):
        self.dss_instance.Solution.MaxControlIterations(max_iterations)

    def set_stepsize(self, step_in_min):
        self.dss_instance.Solution.StepSizeMin(step_in_min)

    def post_redirect(self, dss_file_path: Path):
        """ Redirect this file."""
        self.dss_instance.run_command(f"Redirect {str(dss_file_path.absolute())}")
        self.recalc()
        self.solve()

    def recalc(self):
        """ Method to recal and solve. """
        self.dss_instance.execute_dss_command("calcv")

    def solve(self):

        self.dss_instance.Solution.Number(1)
        self.dss_instance.Solution.Solve()
        return self.dss_instance.Solution.Converged()

    def set_simulation_time(self, sim_time, profile_start_time):

        time_diff = sim_time - profile_start_time
        total_seconds = time_diff.total_seconds()
        hours = int(total_seconds/3600)
        seconds = total_seconds - hours*3600
        self.dss_instance.Solution.Hour(hours)
        self.dss_instance.Solution.Seconds(seconds)

