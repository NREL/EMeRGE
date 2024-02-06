"""
Create a geoJSON for a feeder model
"""

# standard imports
from pathlib import Path
# from typing import List, Dict, String, Union

# util librarys
# from pyproj import Transformer
import pyproj


# internal imports
from emerge.utils.util import validate_path, write_file

def create_feeder_geojson(
    dss_instance,
    output_folder,
    # feeder_file_id
):
    print("################################################################  ")
    print(f"Parsing Power System Model Entities")
    print("################################################################  ")

    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)
    validate_path(output_folder)
    # feeder_file_id = 'feeder_id'

    # Let's get all the buses
    bus_geojson = {"type": "FeatureCollection", "features": []}
    
    # Get all the busnames, loop over them and find the 
    # x,y coordinates 
    all_buses = dss_instance.Circuit.AllBusNames()
    feederID = dss_instance.Circuit.Name()
    bus_coord_dict = {}
    # print("################################################################  ")
    print(f"Parsing Power System Model: Buses :: {len(all_buses)}")
    # print("################################################################  ")
    for bus in all_buses:
        dss_instance.Circuit.SetActiveBus(bus)
        x, y = dss_instance.Bus.X(), dss_instance.Bus.Y()
        lon, lat = convert_local_coords_to_WGS84([x,y], "EPSG:2925") # PROJCS["NAD83(HARN) / Virginia South

        bus_coord_dict[bus] = {
            'longitude': lon,
            'latitude': lat
        }

        bus_geojson['features'].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [lon, lat]
                },
                "properties": {
                    "entity": 'Bus',
                    "name": bus,
                    "feederID" : feederID,
                    "kV_base" : dss_instance.Bus.kVBase()
                }
            }
        )
    # write_file(bus_geojson, output_folder / 'buses.json')

    # Get all the line sections
    # print("################################################################  ")
    print(f"Parsing Power System Model: Lines :: {dss_instance.Lines.Count()}")
    # print("################################################################  ")
    lines_geojson = {"type": "FeatureCollection", "features": []}
    flag = dss_instance.Lines.First()

    while flag:
        line_name = dss_instance.Lines.Name()
        bus1, bus2 = dss_instance.Lines.Bus1().split('.')[0], dss_instance.Lines.Bus2().split('.')[0]
        n_customers = dss_instance.Lines.TotalCust()
        line_length = dss_instance.Lines.Length()
        phases = dss_instance.Lines.Phases()


        lines_geojson['features'].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [bus_coord_dict[bus1]['longitude'], bus_coord_dict[bus1]['latitude']],
                        [bus_coord_dict[bus2]['longitude'], bus_coord_dict[bus2]['latitude']]
                    ],
                },
                "properties": {
                    "entity": 'Line',
                    "name": line_name,
                    # "feederID" : feederID,
                    "n_customers": n_customers,
                    "bus1": bus1,
                    "bus2": bus2,
                    "line_length" : line_length,
                    "phases": phases
                }
            }
        )

        flag = dss_instance.Lines.Next()
    
    # write_file(lines_geojson, output_folder / 'lines.json')

    # Get all transformers
    # print("################################################################  ")
    print(f"Parsing Power System Model: Transformers :: {dss_instance.Transformers.Count()}")
    # print("################################################################  ")
    transformer_geojson = {"type": "FeatureCollection", "features": []}
    flag = dss_instance.Transformers.First()

    while flag:
        transformer_name = dss_instance.CktElement.Name()
        bus1, bus2 = dss_instance.CktElement.BusNames()[:2]
        bus1, bus2 = bus1.split('.')[0], bus2.split('.')[0]
        transformer_geojson['features'].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [bus_coord_dict[bus1]['longitude'], bus_coord_dict[bus1]['latitude']],
                },
                "properties": {
                    "entity": 'Transformer',
                    "name": transformer_name,
                    # "feederID" : feederID,
                    "bus1": bus1,
                    "bus2": bus2,
                    "kva": dss_instance.Transformers.kVA(),
                    # "kvs": dss_instance.Transformers.kvs(),
                    # "kvas": dss_instance.Transformers.kVAS(),
                    "windings": dss_instance.Transformers.NumWindings(),
                    # "phases": dss_instance.Transformers.NumPhases()




                }
            }
        )

        flag = dss_instance.Transformers.Next()
    
    # write_file(transformer_geojson, output_folder / 'transformers.json')

    # Get all loads
    # print("################################################################  ")
    print(f"Parsing Power System Model: Loads :: {dss_instance.Loads.Count()}")
    # print("################################################################  ")
    load_geojson = {"type": "FeatureCollection", "features": []}
    flag = dss_instance.Loads.First()
    while flag:
        load_name = dss_instance.CktElement.Name()
        bus1 = dss_instance.CktElement.BusNames()[0]
        bus1 = bus1.split('.')[0]
        load_geojson['features'].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [bus_coord_dict[bus1]['longitude'], bus_coord_dict[bus1]['latitude']],
                },
                "properties": {
                    "entity": 'Load',
                    "name": load_name,
                    # "feederID" : feederID,
                    "bus": bus1,
                    "kw": dss_instance.Loads.kW(),
                    "kV": dss_instance.Loads.kV(),
                    "kvar": dss_instance.Loads.kvar(),
                    "Vmin_pu": dss_instance.Loads.Vminpu(),
                    "Vmax_pu": dss_instance.Loads.Vmaxpu(),
                    "phases": dss_instance.Loads.Phases()
                }
            }
        )

        flag = dss_instance.Loads.Next()
    
    # write_file(load_geojson, output_folder / 'loads.json')
        
    # Get all capacitors
    # print("################################################################  ")
    print(f"Parsing Power System Model: Capacitors :: {dss_instance.Capacitors.Count()}")
    # print("################################################################  ")
    capacitors_geojson = {"type": "FeatureCollection", "features": []}
    flag = dss_instance.Capacitors.First()
    while flag:
        capacitor_name = dss_instance.CktElement.Name()
        bus1 = dss_instance.CktElement.BusNames()[0]
        bus1 = bus1.split('.')[0]
        load_geojson['features'].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [bus_coord_dict[bus1]['longitude'], bus_coord_dict[bus1]['latitude']],
                },
                "properties": {
                    "entity": 'Capacitor',
                    "name": capacitor_name,
                    # "feederID" : feederID,
                    "bus": bus1,
                    "kvar": dss_instance.Capacitors.kvar(),
                    "kV": dss_instance.Capacitors.kV()
                }
            }
        )

        flag = dss_instance.Capacitors.Next()
    
    # write_file(capacitors_geojson, output_folder / 'Capacitors.json')



    # print("################################################################  ")
    print(f"Writing combined geoJSON file.")
    # For input openDSS model file, Option to write out to single file (feeder) vs. write out individual feeder components (buses.json, lines.json, etc. )
    combined_assets = {
        "type" : "FeatureCollection",
        "features" : [ *bus_geojson["features"], *lines_geojson["features"], *transformer_geojson["features"], *load_geojson["features"], *capacitors_geojson['features'] ] # add *capacitors_geojson 
    }
    num_asset = len(combined_assets["features"])
    file_name = f"{feederID}.json"
    write_file(combined_assets, output_folder / file_name )

    # print("################################################################  ")
    print(f"Done. Number of Power Systems Entites Parsed: {num_asset}")
    print("################################################################  ")



def convert_local_coords_to_WGS84(coordinates, base_projection = "EPSG:2925"): # : List[float], : String  -> List[float]
    """ Converts openDSS local coordinates (x,y) to (lon, lat)
        Uses "EPSG:4236" (i.e., WGS84) projection from provided base_projection string "EPSG:####"
    """
    # transformer = Transformer.from_crs(crs_4326, crs_26917)
    # transformer = Transformer.from_crs(4326, 26917)
    transformer = pyproj.Transformer.from_crs(base_projection, "EPSG:4326") # Sets up coordinate transformer function to convert from base to WGS84
    lat, lon =  transformer.transform(coordinates[0], coordinates[1])
    # print(f"Convert Coords from: {coordinates} to: {[lon, lat]} ")
    return lon, lat 