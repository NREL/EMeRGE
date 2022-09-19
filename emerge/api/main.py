# standard imports
from pathlib import Path

# third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tinydb import Query
import numpy as np

# internal imports
from emerge.utils.util import read_file
from emerge.db.db_handler import TinyDBHandler
from emerge.api import config_model
from emerge.api import utils

config_json = Path(__file__).absolute().parents[0] / "config.json"
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
query = Query()
db_snapshot = TinyDBHandler(config.snapshot_metrics_db)
db_timeseries = TinyDBHandler(config.timeseries_metrics_db)

scenario_metrics = {
    "unity_pf": {},
    "voltvar": {},
    "voltvar_night_off": {}
}
scenario_paths = {
    "unity_pf": Path(config.scenario_metrics_db),
    "voltvar": Path(config.scenario_metrics_vvar),
    "voltvar_night_off": Path(config.scenario_metrics_vvar_nighttime)
}
for scenario_name, scenario_path in scenario_paths.items():
    for filepath in scenario_path.iterdir():
        if filepath.suffix == ".json":
            scenario_metrics[scenario_name][filepath.name.split(".")[0]] = TinyDBHandler(
                filepath
            )
        
    scenario_metrics[scenario_name]['scenario_0_0'] = TinyDBHandler(config.timeseries_metrics_db)


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


@app.get("/scenarios/timeseries_asset/{metric_name}")
def get_scenario_system_metrics(metric_name: str):

    json_content = []
    
    for func in [{"name": "max", "func": np.nanmax}, 
                {"name": "min", "func": np.nanmin},
                {"name": "90-percentile", "func": np.percentile, "args": [90]}, 
                {"name": "mean", "func": np.nanmean},
                {"name": "98-percentile", "func": np.percentile, "args": [98]},
                {"name": "99-percentile", "func": np.percentile, "args": [99]}]:
        
        metrics = []
        for name, db_ in scenario_metrics["unity_pf"].items():
            
            query_result = db_.db.search(
                query.type == "metrics" and query.name == metric_name
            )
            
            if query_result:
                query_result = query_result[0]["data"]
                
                metric_values = list(query_result.values())
                metrics.append(
                    {"metric": func["func"](metric_values) if "args"  not in \
                        func else func["func"](metric_values, *func['args']), 
                    "name": name.split("_")[2] + "%"}
                )
            
        if metrics:
            metrics = sorted(
                metrics, key=lambda d: float(d["name"].split("%")[0])
            )
        

            json_content.append(
                {
                    "type": "scatter",
                    "x": [metric["name"] for metric in metrics],
                    "y": [metric["metric"] for metric in metrics],
                    "name": func["name"]
                },
            )
            

    return json_content


@app.get("/scenarios/timeseries/{metric_name}")
def get_scenario_system_metrics(metric_name: str):

    json_content = []
    for which_power in ['active_power', 'reactive_power']:
        for scenario_name, scenario_metrics_db in scenario_metrics.items():
            metrics = []
            
            for name, db_ in scenario_metrics_db.items():
                metric = db_.db.search(
                    query.type == "metrics" and query.name == metric_name
                )

                if metric:
                    metric = metric[0]["data"][which_power]
                    metrics.append(
                        {"metric": metric, "name": name.split("_")[2] + "%"}
                    )
            

            if metrics:
                metrics = sorted(
                    metrics, key=lambda d: float(d["name"].split("%")[0])
                )
        

                json_content.append(
                    {
                        "type": "scatter",
                        "x": [metric["name"] for metric in metrics],
                        "y": [metric["metric"] for metric in metrics],
                        "name": scenario_name + '__' + which_power
                    },
                )
                

    return json_content


@app.get("/scenarios/system_metrics")
def get_scenario_system_metrics():
    
    json_content = []
    
    for metric_name in ['SARDI_voltage', 'SARDI_aggregated', 'SARDI_line', 'SARDI_transformer']:
        
        for scenario_name, scenario_metrics_db in scenario_metrics.items():
            metrics = []
            for name, db_ in scenario_metrics_db.items():
                
                metric = db_.db.search(
                    query.type == "metrics" and query.name == metric_name
                )

                if metric:
                    metric = metric[0]["data"][metric_name.lower()]

                    metrics.append(
                        {"metric": metric, "name": name.split("_")[2] + "%"}
                    )
            
            if metrics:
                metrics = sorted(
                    metrics, key=lambda d: float(d["name"].split("%")[0])
                )
        

                json_content.append(
                    {
                        "type": "scatter",
                        "x": [metric["name"] for metric in metrics],
                        "y": [metric["metric"] for metric in metrics],
                        "name": scenario_name + '__' + metric_name 
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

@app.get("/snapshots/line_loading")
def get_snapshot_line_loading():

    metric_data = db_snapshot.db.search(
        query.type == "snapshot_lineloading_for_heatmap"
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

@app.get("/snapshots/xfmr_loading")
def get_snapshot_xfmr_loading():
 
    metric_data = db_snapshot.db.search(
        query.type == "snapshot_xfmrloading_for_heatmap"
    )[0]["data"]

    json_content = [
        {
            "coordinates": xfmr_to_coordinate_mapping[key.replace('transformer.', 'Transformer.')],
            "weight": value
        }
        for key, value in metric_data.items()
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

@app.get("/snapshots/voltage-by-distance")
def get_voltage_by_distance():

    voltage_by_distance = db_snapshot.db.search(query.type == "snapshot_voltage_by_distance")[0]

    voltage_by_phase = {}
    json_content = []
    for distance, phase, pu in zip(voltage_by_distance["data"]["Distance from substation (km)"],
        voltage_by_distance["data"]["Phase"], voltage_by_distance["data"]["Voltage (pu)"]):
        if phase not in voltage_by_phase:
            voltage_by_phase[phase] = {
                "distance": [],
                "pu": []
            }
        voltage_by_phase[phase]['distance'].append(distance)
        voltage_by_phase[phase]['pu'].append(pu)

    for key, subdict in voltage_by_phase.items():
        json_content.append(
            {
                "x": subdict['distance'],
                "y": subdict['pu'],
                "name": f"phase_{key}",
                "mode": 'markers',
                "type": "scatter"
            }
        )

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


