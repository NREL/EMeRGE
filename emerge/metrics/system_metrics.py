""" Module for managing computation of system level metrics. """
import networkx as nx
import opendssdirect as odd
import polars as pl

from emerge.metrics import observer
from emerge.simulator import powerflow_results
from emerge.utils import dss_util
from emerge.metrics import data_model
from emerge.network import asset_metrics


def _get_unimpacted_buses(graph: nx.Graph, impacted_edges: list[str], source_bus: str):
    """Internal function to return unimpacted buses."""

    graph_copy = nx.Graph()
    edge_to_be_removed = []
    for edge in graph.edges():
        graph_copy.add_edge(*edge)
        edge_data = graph.get_edge_data(*edge)
        if edge_data and "name" in edge_data and edge_data["name"] in impacted_edges:
            edge_to_be_removed.append(edge)

    graph_copy.remove_edges_from(edge_to_be_removed)
    connected_buses = nx.node_connected_component(graph_copy, source_bus)
    return connected_buses


def _get_voltage_impacted_buses(voltage_df: pl.DataFrame, ov_th: float, uv_th: float) -> list[str]:
    """Internal function to return list of buses impacted by voltage violations."""
    v_col = pl.col("voltage(pu)")
    return (
        voltage_df.filter((v_col > ov_th) & (v_col < uv_th) & (v_col > 0))
        .group_by("busname")
        .agg(v_col.mean())["busname"]
        .to_list()
    )


class TimeseriesTotalLoss(observer.MetricObserver):
    """Class for computing total loss.

    Attributes:
        active_power (float): Time series active power
        reactive_power (float): Time series reactive power
    """

    def __init__(self):
        self.active_power = []
        self.reactive_power = []

    def compute(self):
        """Refer to base class for more details."""
        timestep = odd.Solution.StepSize() / (3600)
        sub_losses = odd.Circuit.Losses()

        self.active_power.append((sub_losses[0]) * timestep / 1000)
        self.reactive_power.append((sub_losses[1]) * timestep / 1000)

    def get_metric(self):
        """Refer to base class for more details."""
        return {"active_power": self.active_power, "reactive_power": self.reactive_power}


class TimeseriesTotalPower(observer.MetricObserver):
    """Class for timeseries total power.

    Attributes:
        active_power (float): Time series active power
        reactive_power (float): Time series reactive power
    """

    def __init__(self):
        self.active_power = []
        self.reactive_power = []

    def compute(self):
        """Refer to base class for more details."""
        timestep = odd.Solution.StepSize() / (3600)
        sub_power = odd.Circuit.TotalPower()

        self.active_power.append((-sub_power[0]) * timestep / 1000)
        self.reactive_power.append((-sub_power[1]) * timestep / 1000)

    def get_metric(self):
        """Refer to base class for more details."""
        return {"active_power": self.active_power, "reactive_power": self.reactive_power}


class TimeseriesTotalPVPower(observer.MetricObserver):
    """Class for computing time series total pv power.

    Attributes:
        active_power (float): Time series active power
        reactive_power (float): Time series reactive power
    """

    def __init__(self):
        self.active_power = []
        self.reactive_power = []

    def compute(self):
        """Refer to base class for more details."""
        timestep = odd.Solution.StepSize() / (3600)
        pv_df = powerflow_results.get_pv_power_dataframe()
        if not pv_df.empty:
            pv_power = pv_df.sum().to_dict()
            self.active_power.append(pv_power["active_power"] * timestep / 1000)
            self.reactive_power.append(pv_power["reactive_power"] * timestep / 1000)
        else:
            self.active_power.append(0)
            self.reactive_power.append(0)

    def get_metric(self):
        """Refer to base class for more details."""
        return {"active_power": self.active_power, "reactive_power": self.reactive_power}


class TotalLossEnergy(observer.MetricObserver):
    """Class for computing total loss.

    Attributes:
        total_loss (float): Store for total energy
    """

    def __init__(self):
        self.total_loss = {"active_power": 0, "reactive_power": 0}

    def compute(self):
        """Refer to base class for more details."""
        timestep = odd.Solution.StepSize() / (3600)
        sub_losses = odd.Circuit.Losses()

        self.total_loss["active_power"] += (sub_losses[0]) * timestep / 1000000
        self.total_loss["reactive_power"] += (sub_losses[1]) * timestep / 1000000

    def get_metric(self):
        """Refer to base class for more details."""
        return self.total_loss


class TotalEnergy(observer.MetricObserver):
    """Class for computing total energy.

    Attributes:
        total_energy (float): Store for total energy
    """

    def __init__(self, export_only: bool = False, import_only: bool = False):
        self.total_energy = {"active_power": 0, "reactive_power": 0}
        self.export_only = export_only
        self.import_only = import_only

    def compute(self):
        """Refer to base class for more details."""
        timestep = odd.Solution.StepSize() / (3600)
        sub_power = odd.Circuit.TotalPower()

        if self.export_only and not self.import_only and sub_power[0] < 0:
            return

        if self.import_only and not self.export_only and sub_power[0] > 0:
            return

        self.total_energy["active_power"] += (-sub_power[0]) * timestep / 1000
        self.total_energy["reactive_power"] += (-sub_power[1]) * timestep / 1000

    def get_metric(self):
        """Refer to base class for more details."""
        return self.total_energy


class TotalPVGeneration(observer.MetricObserver):
    """Class for computing total energy in MWh.

    Attributes:
        pv_energy (float): Store for total energy
    """

    def __init__(self):
        self.pv_energy = {"active_power": 0, "reactive_power": 0}

    def compute(self):
        """Refer to base class for more details."""
        timestep = odd.Solution.StepSize() / (3600)
        pv_df = powerflow_results.get_pv_power_dataframe()
        if not pv_df.empty:
            pv_power = pv_df.sum().to_dict()
            self.pv_energy["active_power"] += pv_power["active_power"] * timestep / 1000
            self.pv_energy["reactive_power"] += pv_power["reactive_power"] * timestep / 1000

    def get_metric(self):
        """Refer to base class for more details."""
        return self.pv_energy


class SARDI_aggregated(observer.MetricObserver):
    """Class for computing SARDI aggregated metric.

    Attributes:
        loading_limit (ThermalLoadingLimit): Instance of `ThermalLoadingLimit`
            data model.
        sardi_transformer (float): SARDI_line metric
        counter (int): Counter for keeping track how number
            of times compute function is called
        network (nx.Graph): Networkx graph representing
            distribution network
    """

    def __init__(self, loading_limit: float = 1.0, voltage_limit: dict | None = None):
        """Constructor for `SARDI_line` class.

        Args:
            loading_limit (float): Per unit loading limit
                used for computing SARDI_line metric.
            voltage_limit (dict): Voltage threshold
        """
        voltage_limit = (
            {"overvoltage_threshold": 1.05, "undervoltage_threshold": 0.95}
            if voltage_limit is None
            else voltage_limit
        )

        self.loading_limit = data_model.ThermalLoadingLimit(threshold=loading_limit)
        self.voltage_limit = data_model.VoltageViolationLimit(**voltage_limit)
        self.sardi_aggregated = 0
        self.counter = 0

    def _get_initial_dataset(self):
        """Get initial dataset for computing the metric."""
        self.network = asset_metrics.networkx_from_opendss_model()
        self.load_bus_map = dss_util.get_bus_load_dataframe().set_index("busname")
        self.substation_bus = dss_util.get_source_node()
        self.bus_load_flag_df = dss_util.get_bus_load_flag()

    def compute(self):
        """Refer to base class for more details."""

        # Get line loading dataframe
        line_loading_df = powerflow_results.get_loading_dataframe()
        voltage_df = powerflow_results.get_voltage_dataframe()

        if not self.counter:
            self._get_initial_dataset()

        bus_with_voltage_violations = _get_voltage_impacted_buses(
            voltage_df,
            self.voltage_limit.overvoltage_threshold,
            self.voltage_limit.undervoltage_threshold,
        )

        overloaded_branches = line_loading_df.filter(
            pl.col("loading(pu)") > self.loading_limit.threshold
        )["branch"].to_list()
        total_impacted_load_buses = bus_with_voltage_violations
        if overloaded_branches:
            connected_buses = _get_unimpacted_buses(
                self.network, overloaded_branches, self.substation_bus
            )
            impacted_buses = self.bus_load_flag_df.loc[
                self.bus_load_flag_df.index.difference(connected_buses)
            ]
            impacted_load_buses = set(impacted_buses[impacted_buses["is_load"] == 1].index)
            total_impacted_load_buses = impacted_load_buses.union(bus_with_voltage_violations)

        total_load = odd.Loads.Count()
        affected_loads = list(
            set(self.load_bus_map.loc[list(total_impacted_load_buses)]["loadname"])
        )
        self.sardi_aggregated += len(affected_loads) * 100 / total_load
        self.counter += 1

    def get_metric(self):
        """Refer to base class for more details."""
        return {
            "sardi_aggregated": self.sardi_aggregated / self.counter if self.counter > 0 else 0
        }


class SARDI_line(observer.MetricObserver):
    """Class for computing SARDI line metric.

    Attributes:
        loading_limit (ThermalLoadingLimit): Instance of `ThermalLoadingLimit`
            data model.
        sardi_line (float): SARDI_line metric
        counter (int): Counter for keeping track how number
            of times compute function is called
        network (nx.Graph): Networkx graph representing
            distribution network
    """

    def __init__(self, loading_limit: float = 1.0):
        """Constructor for `SARDI_line` class.

        Args:
            loading_limit (float): Per unit loading limit
                used for computing SARDI_line metric.
        """

        self.loading_limit = data_model.ThermalLoadingLimit(threshold=loading_limit)
        self.sardi_line = 0
        self.counter = 0

    def _get_initial_dataset(self):
        """Get initial dataset for computing the metric."""
        self.network = asset_metrics.networkx_from_opendss_model()
        self.substation_bus = dss_util.get_source_node()
        self.bus_load_flag_df = dss_util.get_bus_load_flag()
        self.load_bus_map = dss_util.get_bus_load_dataframe().set_index("busname")

    def compute(self):
        """Refer to base class for more details."""

        # Get line loading dataframe
        line_loading_df = powerflow_results.get_loading_dataframe()

        if not self.counter:
            self._get_initial_dataset()

        overloaded_lines = line_loading_df.filter(
            pl.col("loading(pu)") > self.loading_limit.threshold
        )["branch"].to_list()

        if overloaded_lines:
            connected_buses = _get_unimpacted_buses(
                self.network, overloaded_lines, self.substation_bus
            )
            impacted_buses = self.bus_load_flag_df.loc[
                self.bus_load_flag_df.index.difference(connected_buses)
            ]
            impacted_load_buses = impacted_buses[impacted_buses["is_load"] == 1].index
            affected_loads = set(list(self.load_bus_map.loc[impacted_load_buses]["loadname"]))
            total_load = odd.Loads.Count()
            self.sardi_line += len(affected_loads) * 100 / total_load

        self.counter += 1

    def get_metric(self):
        """Refer to base class for more details."""
        return {"sardi_line": self.sardi_line / self.counter if self.counter > 0 else 0}


class SARDI_voltage(observer.MetricObserver):
    """Class for managing the computation of SARDI voltage metric.

    Attributes:
        upper_threshold (float): Voltage upper threshold
        lower_threshold (float): Voltage lower threshold
        sardi_voltage (float): SARDI voltage metric
        counter (int): Counter for keeping track how number
            of times compute function is called
        load_bus_map (pd.DataFrame): Dataframe containing mapping
            between bus and load
    """

    def __init__(self, upper_threshold: float = 1.05, lower_threshold: float = 0.95):
        """Constructor for SARDI_voltage metric.

        Args:
            upper_threshold (float): Voltage upper threshold
            lower_threshold (float): Voltage lower threshold
        """

        self.upper = upper_threshold
        self.lower = lower_threshold
        self.sardi_voltage = 0
        self.counter = 0

    def compute(self):
        """Refer to base class for more details."""

        # Get voltage dataframe and load bus mapper
        voltage_df = powerflow_results.get_voltage_dataframe()

        if not hasattr(self, "load_bus_map"):
            self.load_bus_map = dss_util.get_bus_load_dataframe().set_index("busname")

        # Filter voltages for load buses only
        # and count the number of overvoltages and undervoltages
        impacted_buses = _get_voltage_impacted_buses(voltage_df, self.upper, self.lower)
        affected_loads = list(set(self.load_bus_map.loc[impacted_buses]["loadname"]))

        self.sardi_voltage += len(affected_loads) * 100 / len(self.load_bus_map)
        self.counter += 1

    def get_metric(self):
        """Refer to base class for more details."""
        return {"sardi_voltage": self.sardi_voltage / self.counter if self.counter > 0 else 0}
