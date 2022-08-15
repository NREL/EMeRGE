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


db_instance = TinyDBHandler(r'C:\Users\KDUWADI\Desktop\NREL_Projects\Tunishia\db.json')
query = Query()

app = FastAPI()

origins = [
    "http://localhost:3001",
]

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
 
    file_path = Path(r'C:\Users\KDUWADI\Desktop\NREL_Projects\Tunishia\output_geojson\buses.json')
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/geojsons/lines")
def get_lines_geojson():
 
    file_path = Path(r'C:\Users\KDUWADI\Desktop\NREL_Projects\Tunishia\output_geojson\lines.json')
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/geojsons/transformers")
def get_transformer_geojson():
 
    file_path = Path(r'C:\Users\KDUWADI\Desktop\NREL_Projects\Tunishia\output_geojson\transformers.json')
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/geojsons/loads")
def get_loads_geojson():
 
    file_path = Path(r'C:\Users\KDUWADI\Desktop\NREL_Projects\Tunishia\output_geojson\loads.json')
    json_content = {
        "type": file_path.name.split('.')[0],
        "data": read_file(file_path)
    }

    return json_content

@app.get("/assets/metrics")
def get_asset_metrics():
    
    asset_metrics = db_instance.db.search(query.type=='asset_metrics')[0]['metrics']
    
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
    
    voltage_for_heatmap = db_instance.db.search(query.type=='snapshot_voltage_for_heatmap')[0]['data']
    # voltage_heatmap_figure = px.density_mapbox(voltage_for_heatmap_df, lat='latitudes', \
    #     lon='longitudes', z='voltage (pu)', radius=10, 
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
    
    voltage_bins = db_instance.db.search(query.type=='snapshot_voltage_bins')
    json_content = [
        {
           "x": arr['data']['Voltage bins'],
           "y": arr['data']['Percentage nodes'],
           "name":  arr['label'],
           "type": "bar"
        } for arr in voltage_bins
    ]

    return json_content

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}