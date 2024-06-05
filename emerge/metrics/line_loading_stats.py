""" Module for computing timeseries line loading stats. """

from typing import Dict, List
import numpy as np

import polars
import opendssdirect as odd

from emerge.metrics import observer
from emerge.simulator import powerflow_results


def get_line_loading_df():
    return powerflow_results.get_loading_dataframe()


class OverloadedLines(observer.MetricObserver):
    """Class for computing time series loading metrics for lines."""

    def __init__(self):
        self.metrics = {}

    def compute(self) -> None:
        df = powerflow_results.get_loading_dataframe()
        loading_dict = dict(zip(df["branch"], df["loading(pu)"]))
        if len(self.metrics) == 0:
            self.metrics = {key: [] for key in loading_dict}

        for line, metric in loading_dict.items():
            self.metrics[line].append(metric)

    def get_metric(self) -> Dict:
        overloaded_lines = {}
        for line, loading_arr in self.metrics.items():
            loading_arr_np = np.array(loading_arr)
            if len(loading_arr_np[loading_arr_np > 1.0]):
                overloaded_lines[line] = loading_arr

        return overloaded_lines


class LineLoadingBins(observer.MetricObserver):
    """Class for computing line loading distribution bins."""

    def __init__(self, bins: List[float]):
        bins = list(set(bins))
        bins.sort()

        if len(bins) < 2:
            raise ValueError(f"{bins} should at least have two unique items.")

        self.metrics = {f">{bins[id]}__<{el}": 0 for id, el in enumerate(bins[1:])}
        self.metrics[f"<{bins[0]}"] = 0
        self.metrics[f">{bins[-1]}"] = 0

    def compute(self) -> None:
        df = get_line_loading_df()
        timestep = odd.Solution.StepSize() / (3600)

        for metric in self.metrics:
            if "__" in metric:
                low_val = float(metric.split("__")[0].split(">")[1])
                high_val = float(metric.split("__")[1].split("<")[1])

                self.metrics[metric] += (
                    len(
                        df.filter(
                            (polars.col("loading(pu)") > low_val)
                            & (polars.col("loading(pu)") < high_val)
                        )
                    )
                    * timestep
                )

            elif "<" in metric and "__" not in metric:
                low_val = float(metric.split("<")[1])
                self.metrics[metric] += (
                    len(df.filter((polars.col("loading(pu)") < low_val))) * timestep
                )

            elif ">" in metric and "__" not in metric:
                high_val = float(metric.split(">")[1])
                self.metrics[metric] += (
                    len(df.filter((polars.col("loading(pu)") > high_val))) * timestep
                )

    def get_metric(self) -> Dict:
        return self.metrics


class LineLoadingStats(observer.MetricObserver):
    """Class for computing line loading statistics."""

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
        df = get_line_loading_df()  # noqa
        for metric in self.metrics:
            if "_" not in metric:
                self.metrics[metric].append(eval(f"df.{metric}()['loading(pu)'][0]"))
            else:
                param = float(metric.split("_")[1])
                self.metrics[metric].append(
                    eval(f"df.{metric.split('_')[0]}({param})['loading(pu)'][0]")
                )

    def get_metric(self) -> Dict:
        return self.metrics
