"""This module contains function to get observers."""

from typing import Annotated, Any, Literal

from pydantic import Field, BaseModel

from emerge.metrics import system_metrics
from emerge.metrics import node_voltage_stats
from emerge.metrics import line_loading_stats


CLASS_MAPPER = {
    "substation_power": system_metrics.TimeseriesTotalPower,
    "total_pvpower": system_metrics.TimeseriesTotalPVPower,
    "total_powerloss": system_metrics.TimeseriesTotalLoss,
    "node_timeseries_voltage": node_voltage_stats.NodeVoltageTimeSeries,
    "node_voltage_stats": node_voltage_stats.NodeVoltageStats,
    "node_voltage_bins": node_voltage_stats.NodeVoltageBins,
    "line_loading_stats": line_loading_stats.LineLoadingStats,
    "line_loading_bins": line_loading_stats.LineLoadingBins,
    "overloaded_lines": line_loading_stats.OverloadedLines,
    "sardi_voltage": system_metrics.SARDI_voltage,
    "sardi_line": system_metrics.SARDI_line,
    "sardi_aggregated": system_metrics.SARDI_aggregated,
}


class MetricEntry(BaseModel):
    """Interface for defining metric entry."""

    export_type: Annotated[
        Literal["csv"],
        Field("csv", description="Export format type. Only csv is supported for now."),
    ]
    file_name: Annotated[str, Field(..., description="File name with extension.")]
    args: Annotated[list[Any], Field([], description="List of arguments if any.")]


class SimulationMetrics(BaseModel):
    """Interface for defining simulation metrics."""

    node_timeseries_voltage: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="node_voltage_timeseries.csv"),
            description="Statistics for node time series voltages.",
        ),
    ]

    node_voltage_stats: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="node_voltage_stats.csv"),
            description="Statistics for node voltages.",
        ),
    ]
    node_voltage_bins: Annotated[
        MetricEntry,
        Field(
            MetricEntry(
                file_name="node_voltage_bins.csv",
                args=[[0.95, 0.96, 0.97, 0.98, 0.99, 1.0, 1.01, 1.02, 1.03, 1.04, 1.05]],
            ),
            description="Distribution for node voltages.",
        ),
    ]
    line_loading_stats: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="line_loading_stats.csv"),
            description="Statistics about thermal loading of line segments.",
        ),
    ]
    line_loading_bins: Annotated[
        MetricEntry,
        Field(
            MetricEntry(
                file_name="line_loading_bins.csv",
                args=[[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 2]],
            ),
            description="Distribution of thermal loading of line segments.",
        ),
    ]
    xfmr_loading_stats: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="xfmr_loading_stats.csv"),
            description="Statistics about thermal loading of distribution transformers.",
        ),
    ]
    xfmr_loading_bins: Annotated[
        MetricEntry,
        Field(
            MetricEntry(
                file_name="xfmr_loading_bins.csv",
                args=[[0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 2]],
            ),
            description="Distribution of thermal loading of distribution transformers.",
        ),
    ]
    substation_power: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="substation_power_timeseries.csv"),
            description="Time series substation power.",
        ),
    ]

    total_pvpower: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="total_pvpower_timeseries.csv"),
            description="Time series total solar power.",
        ),
    ]
    total_powerloss: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="total_loss_timeseries.csv"),
            description="Time series total power loss.",
        ),
    ]
    sardi_voltage: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="sardi_voltage.csv", args=[1.05, 0.95]),
            description="System average risk duration index associated with voltage violation.",
        ),
    ]
    sardi_line: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="sardi_line.csv", args=[1]),
            description="System average risk duration index associated with line thermal violation.",
        ),
    ]
    sardi_transformer: Annotated[
        MetricEntry,
        Field(
            MetricEntry(file_name="sardi_transformer.csv", args=[1]),
            description="System average risk duration index associated with transformer thermal violation.",
        ),
    ]
    sardi_aggregated: Annotated[
        MetricEntry,
        Field(
            MetricEntry(
                file_name="sardi_aggregated.csv",
                args=[1, {"overvoltage_threshold": 1.05, "undervoltage_threshold": 0.95}],
            ),
            description="System average risk duration index for all violations.",
        ),
    ]
    overloaded_lines: Annotated[
        MetricEntry,
        Field(
            MetricEntry(
                file_name="overloaded_lines.csv",
            ),
            description="Overloaded line along with their loadings.",
        ),
    ]
    overloaded_transformers: Annotated[
        MetricEntry,
        Field(
            MetricEntry(
                file_name="overloaded_transformers.csv",
            ),
            description="Overloaded transformers along with their loadings.",
        ),
    ]


def get_observers(metrics: dict) -> dict:
    """Function to return list of observers."""
    observers = {}

    for key, subdict in metrics.items():
        if key in CLASS_MAPPER:
            if "args" not in subdict:
                observers[key] = CLASS_MAPPER[key]()
            else:
                observers[key] = CLASS_MAPPER[key](*subdict["args"])
    return observers
