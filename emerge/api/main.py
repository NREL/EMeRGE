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

config_json = Path(__file__).absolute().parents[0] / 'config.json'
config = config_model.Config.parse_file(config_json)

db_snapshot = TinyDBHandler(config.snapshot_metrics_db)
db_timeseries = TinyDBHandler(config.timeseries_metrics_db)
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


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/assets/geojsons/buses")
def get_buses_geojson():
 
    file_path = Path(config.geojson_path) / 'buses.json'
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/geojsons/lines")
def get_lines_geojson():
 
    file_path = Path(config.geojson_path) / 'lines.json'
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/geojsons/transformers")
def get_transformer_geojson():
 
    file_path = Path(config.geojson_path) / 'transformers.json'
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/geojsons/loads")
def get_loads_geojson():
 
    file_path = Path(config.geojson_path) / 'loads.json'
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/metrics")
def get_asset_metrics():
    
    asset_metrics = db_snapshot.db.search(query.type=='asset_metrics')[0]['metrics']
    
    json_content = [
        {
            "type": key,
            "data": [
                {
                    "metric": m.replace('_', ' '),
                    "value": round(v, 2) 
                } for m,v in value.items()
            ] 
        } for key, value in asset_metrics.items() 
    ]

    return json_content


@app.get("/snapshots/voltage")
def get_snapshots_voltage():
    
    voltage_for_heatmap = db_snapshot.db.search(query.type=='snapshot_voltage_for_heatmap')[0]['data']
    json_content = [
        {
           "coordinates": [lon, lat],
           "weight": voltage
        } for lat, lon, voltage in zip(
            voltage_for_heatmap['latitudes'],
            voltage_for_heatmap['longitudes'],
            voltage_for_heatmap['voltage (pu)']
            )
    ]

    return json_content

@app.get("/snapshots/voltage-distribution")
def get_snapshots_voltage():
    
    voltage_bins = db_snapshot.db.search(query.type=='snapshot_voltage_bins')
    json_content = [
        {
           "x": arr['data']['Voltage bins'],
           "y": arr['data']['Percentage nodes'],
           "name":  arr['label'],
           "type": "bar"
        } for arr in voltage_bins
    ]

    return json_content
