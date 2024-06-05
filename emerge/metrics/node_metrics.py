""" Module for managing computation of node level metrics. """

import pandas as pd

from emerge.metrics import observer
from emerge.metrics import data_model
from emerge.simulator import powerflow_results
from emerge.utils import dss_util


class LLRI(observer.MetricObserver):
    """Class for managing the computation of Line loading risk index (NVRI).

    Attributes:
        loading_threshold (float): Line loading threshol
        llri_metric (float): LLRI metric
        counter (int): Counter for keeping track how number
            of times compute function is called
        line_downward_customers (pd.DataFrame): Dataframe containing mapping
            between line segment and number of downward customers
    """

    def __init__(self, loading_threshold: float = 1.0):
        """Constructor for LLRI metric.

        Args:
            loading_limit (float): Per unit loading limit
                used for computing SARDI_line metric.
        """

        self.loading_limit = data_model.ThermalLoadingLimit(threshold=loading_threshold)

        self.llri_metric = pd.DataFrame()
        self.counter = 0

    def _get_initial_dataset(self):
        """Get initial dataset for computing the metric."""

        self.line_downward_customers = dss_util.get_line_customers()

    def compute(self):
        """Refer to base class for more details."""

        # Get voltage dataframe and load bus mapper
        line_loading_df = powerflow_results.get_loading_dataframe().to_pandas().set_index("branch")

        if not self.counter:
            self._get_initial_dataset()

        ol_flags = line_loading_df["loading(pu)"] > self.loading_limit.threshold
        ol_gamma = line_loading_df[ol_flags] - self.loading_limit.threshold
        ol_gamma = ol_gamma.rename(columns={"loading(pu)": "ol_llri"})

        merged_df = pd.merge(
            self.line_downward_customers,
            ol_gamma,
            how="left",
            left_index=True,
            right_index=True,
        ).fillna(0)

        merged_df["metric"] = merged_df["customers"] * (merged_df["ol_llri"])

        if self.llri_metric.empty:
            self.llri_metric = pd.DataFrame(merged_df["metric"])
        else:
            self.llri_metric = pd.DataFrame(self.llri_metric["metric"] + merged_df["metric"])

        self.counter += 1

    def get_metric(self):
        """Refer to base class for more details."""
        return {
            linename: metric / self.counter if self.counter else 0
            for linename, metric in self.llri_metric.to_dict().get("metric", {}).items()
        }


class NVRI(observer.MetricObserver):
    """Class for managing the computation of Nodal voltage risk index (NVRI).

    Attributes:
        upper_threshold (float): Voltage upper threshold
        lower_threshold (float): Voltage lower threshold
        nvri_metric (float): NVRI metric
        counter (int): Counter for keeping track how number
            of times compute function is called
        bus_load_flag_df (pd.DataFrame): Dataframe containing mapping
            between bus and load flag
    """

    def __init__(self, upper_threshold: float = 1.05, lower_threshold: float = 0.95):
        """Constructor for SARDI_voltage metric.

        Args:
            upper_threshold (float): Voltage upper threshold
            lower_threshold (float): Voltage lower threshold
        """

        self.voltage_limit = data_model.VoltageViolationLimit(
            overvoltage_threshold=upper_threshold,
            undervoltage_threshold=lower_threshold,
        )

        self.nvri_metric = pd.DataFrame()
        self.counter = 0

    def _get_initial_dataset(self):
        """Get initial dataset for computing the metric."""

        self.bus_load_flag_df = dss_util.get_bus_load_flag()

    def compute(self):
        """Refer to base class for more details."""

        # Get voltage dataframe and load bus mapper
        voltage_df = powerflow_results.get_voltage_dataframe().to_pandas().set_index("busname")

        if not self.counter:
            self._get_initial_dataset()

        ov_flags = voltage_df["voltage(pu)"] > self.voltage_limit.overvoltage_threshold
        ov_gamma = voltage_df[ov_flags] - self.voltage_limit.overvoltage_threshold
        ov_gamma = ov_gamma.rename(columns={"voltage(pu)": "ov_nvri"})

        uv_flags = voltage_df["voltage(pu)"] < self.voltage_limit.undervoltage_threshold
        uv_gamma = self.voltage_limit.undervoltage_threshold - voltage_df[uv_flags]
        uv_gamma = uv_gamma.rename(columns={"voltage(pu)": "uv_nvri"})

        merged_df_ = pd.merge(
            self.bus_load_flag_df,
            ov_gamma,
            how="left",
            left_index=True,
            right_index=True,
        ).fillna(0)
        merged_df = pd.merge(
            merged_df_, uv_gamma, how="left", left_index=True, right_index=True
        ).fillna(0)

        merged_df["metric"] = merged_df["is_load"] * (merged_df["ov_nvri"] + merged_df["uv_nvri"])

        ## Deal with duplicate indexes
        merged_df = merged_df[~merged_df.index.duplicated(keep="first")]

        if self.nvri_metric.empty:
            self.nvri_metric = pd.DataFrame(merged_df["metric"])
        else:
            self.nvri_metric = pd.DataFrame(self.nvri_metric["metric"] + merged_df["metric"])

        self.counter += 1

    def get_metric(self):
        """Refer to base class for more details."""
        return {
            busname: metric / self.counter if self.counter else 0
            for busname, metric in self.nvri_metric.to_dict().get("metric", {}).items()
        }
