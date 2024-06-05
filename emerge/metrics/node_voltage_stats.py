""" Module for computing timeseries voltage stats. """

from typing import List

import opendssdirect as odd
import polars

from emerge.metrics import observer
from emerge.simulator import powerflow_results


def get_voltage_df():
    return powerflow_results.get_voltage_dataframe()


class NodeVoltageTimeSeries(observer.MetricObserver):
    def __init__(self):
        self.metrics = {}

    def compute(self) -> None:
        df = powerflow_results.get_voltage_dataframe()
        if not self.metrics:
            self.metrics = {busname: [] for busname in df.index}
        for key, value in df.to_dict()["voltage(pu)"].items():
            self.metrics[key].append(value)

    def get_metric(self) -> dict:
        return self.metrics


class NodeVoltageStats(observer.MetricObserver):
    """Class for computing node voltage statistical metrics."""

    def __init__(self):
        self.metrics = {
            metric: []
            for metric in [
                "min",
                "max",
                "median",
                "mean",
                "quantile_0.1",
                "quantile_0.25",
                "quantile_0.75",
                "quantile_0.90",
            ]
        }

    def compute(self) -> None:
        df = get_voltage_df()  # noqa
        for metric in self.metrics:
            if "_" not in metric:
                self.metrics[metric].append(eval(f"df.{metric}()['voltage(pu)'][0]"))
            else:
                param = float(metric.split("_")[1])
                self.metrics[metric].append(
                    eval(f"df.{metric.split('_')[0]}({param})['voltage(pu)'][0]")
                )

    def get_metric(self) -> dict:
        return self.metrics


class NodeVoltageBins(observer.MetricObserver):
    """Class for computing node voltage statistical metrics."""

    def __init__(self, bins: List[float]):
        bins = list(set(bins))
        bins.sort()

        if len(bins) < 2:
            raise ValueError(f"{bins} should at least have two unique items.")

        self.metrics = {f">{bins[id]}__<{el}": 0 for id, el in enumerate(bins[1:])}
        self.metrics[f"<{bins[0]}"] = 0
        self.metrics[f">{bins[-1]}"] = 0

    def compute(self) -> None:
        df = get_voltage_df()
        timestep = odd.Solution.StepSize() / (3600)

        for metric in self.metrics:
            if "__" in metric:
                low_val = float(metric.split("__")[0].split(">")[1])
                high_val = float(metric.split("__")[1].split("<")[1])

                self.metrics[metric] += (
                    len(
                        df.filter(
                            (polars.col("voltage(pu)") > low_val)
                            & (polars.col("voltage(pu)") < high_val)
                        )
                    )
                    * timestep
                )

            elif "<" in metric and "__" not in metric:
                low_val = float(metric.split("<")[1])
                self.metrics[metric] += (
                    len(df.filter((polars.col("voltage(pu)") < low_val))) * timestep
                )

            elif ">" in metric and "__" not in metric:
                high_val = float(metric.split(">")[1])
                self.metrics[metric] += (
                    len(df.filter((polars.col("voltage(pu)") > high_val))) * timestep
                )

    def get_metric(self) -> dict:
        return self.metrics
