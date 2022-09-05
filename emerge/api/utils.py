
""" Module containing utility functions for API. """

from emerge.utils.util import read_file

def get_map_center(buses_file_path: str):
    """ Function to get map centre from bus geojson file. """

    buses_geojson = read_file(buses_file_path)
    longitudes, latitudes = [], []
    for feature in buses_geojson['features']:
        coordinates = feature["geometry"]["coordinates"]
        longitudes.append(coordinates[0])
        latitudes.append(coordinates[1])

    return {
        'longitude': sum(longitudes)/len(longitudes) if longitudes else 0,
        'latitude': sum(latitudes)/len(latitudes) if latitudes else 0
    }

def buses_coordinate_mapping(buses_file_path: str):
    """ Function to get mapping formbus and coordinate. """

    buses_geojson = read_file(buses_file_path)
    buses_mapping  = {}
    for feature in buses_geojson['features']:
        bus_name = feature["properties"]["name"]
        coordinates = feature["geometry"]["coordinates"]
        buses_mapping[bus_name] = coordinates

    return buses_mapping

def lines_coordinate_mapping(lines_geojson_path: str):
    """ Function to compute mapping for line segment and coordinate. """
    
    lines_geojson = read_file(lines_geojson_path)
    lines_mapping  = {}
    for feature in lines_geojson['features']:
        line_name = feature["geometry"]["properties"]["name"]
        coordinates = feature["geometry"]["coordinates"]
        lines_mapping[line_name] = coordinates

    return lines_mapping

def transformer_coordinate_mapping(transformer_geojson_path: str):
    """ Function to compute mapping for transformer and coordinate. """
    
    xfmr_geojson = read_file(transformer_geojson_path)
    xfmr_mapping  = {}
    for feature in xfmr_geojson['features']:
        trans_name = feature["geometry"]["properties"]["name"]
        coordinates = feature["geometry"]["coordinates"]
        xfmr_mapping[trans_name] = coordinates

    return xfmr_mapping

