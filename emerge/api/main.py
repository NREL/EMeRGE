# standard imports
from typing import Union
from pathlib import Path

# third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tinydb import Query

# internal imports
from emerge.utils.util import read_file
from emerge.db.db_handler import TinyDBHandler
from emerge.api import config_model
from emerge.api import utils

config_json = Path(__file__).absolute().parents[0] / "config_1.json"
config = config_model.Config.parse_file(config_json)

buses_to_coordinate_mapping = utils.buses_coordinate_mapping(
    Path(config.geojson_path) / "buses.json"
)
lines_to_coordinate_mapping = utils.lines_coordinate_mapping(
    Path(config.geojson_path) / "lines.json"
)
xfmr_to_coordinate_mapping = utils.lines_coordinate_mapping(
    Path(config.geojson_path) / "transformers.json"
)
map_center = utils.get_map_center(Path(config.geojson_path) / "buses.json")

db_snapshot = TinyDBHandler(config.snapshot_metrics_db)
db_timeseries = TinyDBHandler(config.timeseries_metrics_db)

scenario_metrics_db = {}
scenario_path = Path(config.scenario_metrics_db)
for filepath in scenario_path.iterdir():
    if filepath.suffix == ".json":
        scenario_metrics_db[filepath.name.split(".")[0]] = TinyDBHandler(
            filepath
        )
scenario_metrics_db['scenario_0_0'] = TinyDBHandler(config.timeseries_metrics_db)

query = Query()

# Fast API setup
app = FastAPI()
origins = [config.ui_url]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/scenarios/system_metrics")
def get_scenario_system_metrics():

    json_content = []
    for metric_name in ['SARDI_voltage', 'SARDI_aggregated', 'SARDI_line', 'SARDI_transformer']:
        metrics = []
        for name, db_ in scenario_metrics_db.items():
            
            metric = db_.db.search(
                query.type == "metrics" and query.name == metric_name
            )[0]["data"][metric_name.lower()]
            metrics.append(
                {"metric": metric, "name": name.split("_")[2] + "%"}
            )
          

        metrics = sorted(
            metrics, key=lambda d: float(d["name"].split("%")[0])
        )
   

        json_content.append(
            {
                "type": "scatter",
                "x": [metric["name"] for metric in metrics],
                "y": [metric["metric"] for metric in metrics],
                "name": metric_name
            },
        )
            

    return json_content


@app.get("/assets/geojsons/buses")
def get_buses_geojson():

    file_path = Path(config.geojson_path) / "buses.json"
    json_content = {
        "type": file_path.name.split(".")[0],
        "data": read_file(file_path),
    }

    return json_content


@app.get("/assets/geojsons/lines")
def get_lines_geojson():

    file_path = Path(config.geojson_path) / "lines.json"
    json_content = {
        "type": file_path.name.split(".")[0],
        "data": read_file(file_path),
    }

    return json_content


@app.get("/assets/geojsons/transformers")
def get_transformer_geojson():

    file_path = Path(config.geojson_path) / "transformers.json"
    json_content = {
        "type": file_path.name.split(".")[0],
        "data": read_file(file_path),
    }

    return json_content


@app.get("/assets/geojsons/loads")
def get_loads_geojson():

    file_path = Path(config.geojson_path) / "loads.json"
    json_content = {
        "type": file_path.name.split(".")[0],
        "data": read_file(file_path),
    }

    return json_content


@app.get("/assets/metrics")
def get_asset_metrics():

    asset_metrics = db_snapshot.db.search(query.type == "asset_metrics")[0][
        "metrics"
    ]

    json_content = [
        {
            "type": key,
            "data": [
                {"metric": m.replace("_", " "), "value": round(v, 2)}
                for m, v in value.items()
            ],
        }
        for key, value in asset_metrics.items()
    ]

    return json_content


@app.get("/snapshots/voltage")
def get_snapshots_voltage():

    voltage_for_heatmap = db_snapshot.db.search(
        query.type == "snapshot_voltage_for_heatmap"
    )[0]["data"]
    json_content = [
        {"coordinates": [lon, lat], "weight": voltage}
        for lat, lon, voltage in zip(
            voltage_for_heatmap["latitudes"],
            voltage_for_heatmap["longitudes"],
            voltage_for_heatmap["voltage (pu)"],
        )
    ]

    return json_content


@app.get("/snapshots/voltage-distribution")
def get_snapshots_voltage():

    voltage_bins = db_snapshot.db.search(query.type == "snapshot_voltage_bins")
    json_content = [
        {
            "x": arr["data"]["Voltage bins"],
            "y": arr["data"]["Percentage nodes"],
            "name": arr["label"],
            "type": "bar",
        }
        for arr in voltage_bins
    ]

    return json_content


@app.get("/metrics/timeseries/nvri")
def get_timeseries_metric():

    metric_data = db_timeseries.db.search(
        query.type == "metrics" and query.name == "NVRI"
    )[0]["data"]

    json_content = [
        {
            "coordinates": buses_to_coordinate_mapping[key],
            "name": key,
            "data": value,
        }
        for key, value in metric_data.items()
    ]

    return json_content


@app.get("/metrics/timeseries/llri")
def get_timeseries_metric():

    metric_data = db_timeseries.db.search(
        query.type == "metrics" and query.name == "LLRI"
    )[0]["data"]

    json_content = [
        {
            "coordinates": lines_to_coordinate_mapping[key.split(".")[1]],
            "name": key,
            "data": value,
        }
        for key, value in metric_data.items()
    ]

    return json_content


@app.get("/metrics/timeseries/tlri")
def get_timeseries_metric():

    metric_data = db_timeseries.db.search(
        query.type == "metrics" and query.name == "TLRI"
    )[0]["data"]

    json_content = [
        {
            "coordinates": xfmr_to_coordinate_mapping[
                "Transformer." + key.split(".")[1]
            ],
            "name": key,
            "data": value,
        }
        for key, value in metric_data.items()
    ]

    return json_content


@app.get("/metrics/system_metrics")
def get_system_metric():

    metrics = [
        "SARDI_voltage",
        "SARDI_line",
        "SARDI_transformer",
        "SARDI_aggregated",
    ]

    data = []

    for metric in metrics:
        metric_data = db_timeseries.db.search(
            query.type == "metrics" and query.name == metric
        )[0]["data"]
        data.append(
            {
                "name": metric.replace("_", " "),
                "value": metric_data[metric.lower()],
            }
        )

    return data


@app.get("/map_center")
def get_map_center():
    return map_center
