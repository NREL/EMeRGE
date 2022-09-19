""" Model for input config for API. """

from pydantic import BaseModel


class Config(BaseModel):
    snapshot_metrics_db: str
    timeseries_metrics_db: str
    geojson_path: str
    scenario_metrics_db: str
    scenario_metrics_vvar: str
    scenario_metrics_vvar_nighttime: str
    ui_url: str
