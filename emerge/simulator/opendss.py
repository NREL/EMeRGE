""" OpenDSS simulator service for performing power flow."""

from pathlib import Path

import opendssdirect as dss
from loguru import logger


class OpenDSSSimulator:
    def __init__(
        self,
        path_to_master_dss_file,
    ):
        self.case_file = Path(path_to_master_dss_file)
        self.dss_instance = dss

        self.dss_instance.run_command("Clear")
        self.dss_instance.Basic.ClearAll()
        self.execute_dss_command(f"Redirect {self.case_file}")

    def execute_dss_command(self, dss_command: str):
        """Method to run opendss commands."""
        error = self.dss_instance.run_command(dss_command)
        if error:
            logger.error(f"Error executing command {dss_command} >> {error}")
            raise Exception(f"Error executing command {dss_command} >> {error}")
        logger.info(f"Sucessfully executed the command, {dss_command}")
        return error

    def set_frequency(self, frequency: int):
        """Method to set frequency."""
        self.execute_dss_command(f"Set DefaultBaseFrequency={frequency}")

    def set_mode(self, mode: int):
        """Method to set simulation mode.

        For example: 2 means QSTS mode.
        """
        self.dss_instance.Solution.Mode(mode)

    def set_max_iteration(self, max_iterations: int):
        """ "Method to set max iterations."""
        self.dss_instance.Solution.MaxControlIterations(max_iterations)
        self.dss_instance.Solution.MaxIterations(max_iterations)

    def set_stepsize(self, step_in_min: float):
        """Method to set step size."""
        self.dss_instance.Solution.StepSizeMin(step_in_min)

    def post_redirect(self, dss_file_path: Path):
        """Redirect this file."""
        self.execute_dss_command(f"Redirect {str(dss_file_path.absolute())}")
        self.recalc()
        self.solve()

    def recalc(self):
        """Method to recal and solve."""
        self.execute_dss_command("calcv")

    def solve(self):
        self.dss_instance.Solution.Number(1)
        self.dss_instance.Solution.Solve()
        return self.dss_instance.Solution.Converged()

    def set_simulation_time(self, sim_time, profile_start_time):
        time_diff = sim_time - profile_start_time
        total_seconds = time_diff.total_seconds()
        hours = int(total_seconds / 3600)
        seconds = total_seconds - hours * 3600
        self.dss_instance.Solution.Hour(hours)
        self.dss_instance.Solution.Seconds(seconds)
