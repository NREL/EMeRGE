""" Model for input config for API. """

from pydantic import BaseModel


class Config(BaseModel):
    snapshot_metrics_db: str
    timeseries_metrics_db: str
    geojson_path:str
    ui_url: str