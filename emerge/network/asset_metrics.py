"""Extract base level metrics."""

import networkx as nx

import opendssdirect as odd
from emerge.network.data_model import (
    AssetMetrics,
    FeederMetrics,
    LoadAssetMetrics,
    PVAssetMetrics,
    CapacitorAssetMetrics,
    RegulatorsAssetMetrics,
    TransformersAssetMetrics,
)


def opendss_load_metrics_extractor():
    flag = odd.Loads.First()
    kws, kvars = [], []
    while flag:
        kws.append(odd.Loads.kW())
        kvars.append(odd.Loads.kvar())
        flag = odd.Loads.Next()

    return LoadAssetMetrics(
        total_count=odd.Loads.Count(),
        max_kw_capacity=round(max(kws), 3) if kws else 0,
        min_kw_capacity=round(min(kws), 3) if kws else 0,
        min_kvar_capacity=round(min(kvars), 3) if kvars else 0,
        max_kvar_capacity=round(max(kvars), 3) if kvars else 0,
        total_kw_capacity=round(sum(kws), 3) if kws else 0,
        total_kvar_capacity=round(sum(kvars), 3) if kvars else 0,
    )


def opendss_pv_metrics_extractor():
    flag = odd.PVsystems.First()
    kws = []
    while flag:
        kws.append(odd.PVsystems.Pmpp())
        flag = odd.PVsystems.Next()

    return PVAssetMetrics(
        total_count=odd.PVsystems.Count(),
        max_kw_capacity=round(max(kws), 3) if kws else 0,
        min_kw_capacity=round(min(kws), 3) if kws else 0,
        total_kw_capacity=round(sum(kws), 3) if kws else 0,
    )


def opendss_capacitors_metrics_extractor():
    flag = odd.Capacitors.First()
    kvars = []
    while flag:
        kvars.append(odd.Capacitors.kvar())
        flag = odd.PVsystems.Next()

    return CapacitorAssetMetrics(
        total_count=odd.Capacitors.Count(),
        max_kvar_capacity=round(max(kvars), 3) if kvars else 0,
        min_kvar_capacity=round(min(kvars), 3) if kvars else 0,
        total_kvar_capacity=round(sum(kvars), 3) if kvars else 0,
    )


def opendss_regulators_metrics_extractor():
    return RegulatorsAssetMetrics(total_count=odd.RegControls.Count())


def opendss_transformers_metrics_extractor():
    flag = odd.Transformers.First()
    kvas = []
    while flag:
        kvas.append(odd.Transformers.kVA())
        flag = odd.Transformers.Next()

    return TransformersAssetMetrics(
        total_count=odd.Transformers.Count(),
        max_kva_capacity=round(max(kvas), 3) if kvas else 0,
        min_kva_capacity=round(min(kvas), 3) if kvas else 0,
        total_kva_capacity=round(sum(kvas), 3) if kvas else 0,
    )


def networkx_from_opendss_model():
    """Let's create a networkx representation of the model"""
    network = nx.Graph()

    """ Let's add all buses """
    for bus in odd.Circuit.AllBusNames():
        odd.Circuit.SetActiveBus(bus)
        network.add_node(bus, pos=(odd.Bus.X(), odd.Bus.Y()))

    UNIT_MAPPER = {
        0: 0,
        1: 1.60934,
        2: 0.3048,
        3: 1,
        4: 0.001,
        5: 0.0003048,
        6: 0.0000254,
        7: 0.00001,
    }

    """ Let's all line elements to the network """

    for edge_name in ["Line", "Transformer"]:
        odd.Circuit.SetActiveClass(edge_name)
        flag = odd.ActiveClass.First()
        while flag > 0:
            name = odd.CktElement.Name().lower()
            buses = odd.CktElement.BusNames()
            edge_length = (
                0
                if edge_name == "Transformer"
                else UNIT_MAPPER[odd.Lines.Units()] * odd.Lines.Length()
            )

            network.add_edge(
                buses[0].split(".")[0], buses[1].split(".")[0], name=name, length=edge_length
            )
            flag = odd.ActiveClass.Next()

    return network


def get_all_kv_levels():
    flag = odd.Transformers.First()
    kvs = []
    while flag:
        for wdg in range(1, odd.Transformers.NumWindings() + 1):
            odd.Transformers.Wdg(wdg)
            kvs.append(odd.Transformers.kV())
        flag = odd.Transformers.Next()
    return list(set(kvs))


def opendss_feeder_metrics_extractor():
    df = odd.utils.class_to_dataframe("vsource").to_dict()
    source_bus = df["bus1"]["vsource.source"].split(".")[0]

    """ Get networkx representation of opendss model """
    network = networkx_from_opendss_model(odd)

    """ Let's create dfs tree """
    dfs_tree = nx.dfs_tree(network, source=source_bus)

    for edge in dfs_tree.edges():
        edge_data = network[edge[0]][edge[1]]
        dfs_tree[edge[0]][edge[1]]["length"] = edge_data["length"]

    total_feeder_length = nx.dag_longest_path_length(dfs_tree, weight="length", default_weight=0)
    longest_path_length = nx.dag_longest_path(dfs_tree, weight="length", default_weight=0)

    """ Get all the kvs """
    all_kvs = get_all_kv_levels(odd)
    all_kvs.sort()
    secondary_kv, primary_kv = all_kvs[0], all_kvs[1]

    transformer_buses = []

    flag = odd.Transformers.First()

    while flag:
        buses = odd.CktElement.BusNames()

        kvs = []
        for wdg in range(1, odd.Transformers.NumWindings() + 1):
            odd.Transformers.Wdg(wdg)
            kvs.append(odd.Transformers.kV())
        if secondary_kv in kvs:
            transformer_buses.append(buses[0].split(".")[0])
        flag = odd.Transformers.Next()

    secondary_lengths = {}

    for bus in transformer_buses:
        dfs_tree_ = nx.dfs_tree(dfs_tree, source=bus)
        for edge in dfs_tree_.edges():
            edge_data = network[edge[0]][edge[1]]
            dfs_tree_[edge[0]][edge[1]]["length"] = edge_data["length"]

        secondary_length = nx.dag_longest_path_length(dfs_tree_, weight="length", default_weight=0)
        secondary_lengths[bus] = secondary_length

    max_primary_feeder_length = total_feeder_length
    for bus, length in secondary_lengths.items():
        if bus in longest_path_length:
            max_primary_feeder_length = total_feeder_length - length

    secondary_lengths_list = list(secondary_lengths.values())

    return FeederMetrics(
        total_feeder_length_km=round(total_feeder_length, 3),
        max_primary_feeder_length_km=round(max_primary_feeder_length, 3),
        max_secondary_feeder_length_km=round(max(secondary_lengths_list), 3)
        if secondary_lengths_list
        else 0,
        min_secondary_feeder_length_km=round(min(secondary_lengths_list), 3)
        if secondary_lengths_list
        else 0,
        secondary_kv_level=secondary_kv,
        primary_kv_level=primary_kv,
        total_buses=odd.Circuit.NumBuses(),
        total_line_sections=odd.Lines.Count(),
    )


def aggregate_asset_metrics():
    loads = opendss_load_metrics_extractor()
    pvs = opendss_pv_metrics_extractor()
    capacitors = opendss_capacitors_metrics_extractor()
    regs = opendss_regulators_metrics_extractor()
    transformers = opendss_transformers_metrics_extractor()
    feeder = opendss_feeder_metrics_extractor()

    return AssetMetrics(
        loads=loads,
        pvs=pvs,
        capacitors=capacitors,
        regulators=regs,
        transformers=transformers,
        lines=feeder,
    )


def get_coordinates():
    network = networkx_from_opendss_model(odd)
    coordinates = {
        "nodes": {
            "latitudes": [],
            "longitudes": [],
        },
        "edges": {"latitudes": [], "longitudes": []},
    }

    node_data = {node[0]: node[1] for node in network.nodes.data()}
    for edge in network.edges():
        try:
            from_node = node_data[edge[0]]["pos"]
            to_node = node_data[edge[1]]["pos"]
            coordinates["nodes"]["latitudes"].extend([from_node[1], to_node[1]])
            coordinates["nodes"]["longitudes"].extend([from_node[0], to_node[0]])
            coordinates["edges"]["latitudes"].extend([from_node[1], to_node[1], None])
            coordinates["edges"]["longitudes"].extend([from_node[0], to_node[0], None])
        except Exception:
            print(f"{edge} can't get coord info {network.get_edge_data(*edge)}")

    return coordinates
