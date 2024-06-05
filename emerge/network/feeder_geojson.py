"""
Create a geoJSON for a feeder model
"""

from pathlib import Path

from emerge.utils.util import validate_path, write_file


def create_feeder_geojson(dss_instance, output_folder):
    output_folder = Path(output_folder)
    output_folder.mkdir(exist_ok=True)
    validate_path(output_folder)

    # Let's get all the buses
    bus_geojson = {"type": "FeatureCollection", "features": []}

    # Get all the busnames, loop over them and find the
    # x,y coordinates
    all_buses = dss_instance.Circuit.AllBusNames()
    bus_coord_dict = {}
    for bus in all_buses:
        dss_instance.Circuit.SetActiveBus(bus)

        x, y = dss_instance.Bus.X(), dss_instance.Bus.Y()
        bus_coord_dict[bus] = {"longitude": x, "latitude": y}

        bus_geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [x, y]},
                "properties": {"name": bus},
            }
        )
    write_file(bus_geojson, output_folder / "buses.json")

    # Get all the line sections
    lines_geojson = {"type": "FeatureCollection", "features": []}
    flag = dss_instance.Lines.First()
    while flag:
        line_name = dss_instance.Lines.Name()
        bus1, bus2 = (
            dss_instance.Lines.Bus1().split(".")[0],
            dss_instance.Lines.Bus2().split(".")[0],
        )
        n_customers = dss_instance.Lines.TotalCust()
        lines_geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "LineString",
                    "coordinates": [
                        [bus_coord_dict[bus1]["longitude"], bus_coord_dict[bus1]["latitude"]],
                        [bus_coord_dict[bus2]["longitude"], bus_coord_dict[bus2]["latitude"]],
                    ],
                    "properties": {
                        "name": line_name,
                        "n_customers": n_customers,
                        "bus1": bus1,
                        "bus2": bus2,
                    },
                },
            }
        )

        flag = dss_instance.Lines.Next()

    write_file(lines_geojson, output_folder / "lines.json")

    # Get all transformers
    transformer_geojson = {"type": "FeatureCollection", "features": []}
    flag = dss_instance.Transformers.First()
    while flag:
        transformer_name = dss_instance.CktElement.Name()
        bus1, bus2 = dss_instance.CktElement.BusNames()[:2]
        bus1, bus2 = bus1.split(".")[0], bus2.split(".")[0]
        transformer_geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        bus_coord_dict[bus1]["longitude"],
                        bus_coord_dict[bus1]["latitude"],
                    ],
                    "properties": {
                        "name": transformer_name,
                        "bus1": bus1,
                        "bus2": bus2,
                        "kva": dss_instance.Transformers.kVA(),
                    },
                },
            }
        )

        flag = dss_instance.Transformers.Next()

    write_file(transformer_geojson, output_folder / "transformers.json")

    # Get all loads
    load_geojson = {"type": "FeatureCollection", "features": []}
    flag = dss_instance.Loads.First()
    while flag:
        load_name = dss_instance.CktElement.Name()
        bus1 = dss_instance.CktElement.BusNames()[0]
        bus1 = bus1.split(".")[0]
        load_geojson["features"].append(
            {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        bus_coord_dict[bus1]["longitude"],
                        bus_coord_dict[bus1]["latitude"],
                    ],
                    "properties": {
                        "name": load_name,
                        "bus": bus1,
                        "kw": dss_instance.Loads.kW(),
                        "kvar": dss_instance.Loads.kvar(),
                    },
                },
            }
        )

        flag = dss_instance.Loads.Next()

    write_file(load_geojson, output_folder / "loads.json")
