
DEFAULT_CONFIGURATION = {
    "project_path" : "",
    "feeder_name" : "GWC",
    "log_settings": {
        "save_in_file": False,
        "log_folder": "",
        "log_filename":"",
        "clear_old_log_file": True
        },
    "MVA_to_KVA_conversion_for_PT"  : "yes",
    "force_lt_be_three_phase" : "yes",
    "PTrow" :  0,
    "three_phase" : "RYB",
    "single_phase" : ["R","Y","B"],
    "height_of_top_conductor_ht" : 9.0,
    "height_of_top_conductor_lt" : 8.0,
    "ht_spacing" : 1.0,
    "lt_spacing" : 0.47,
    "geomtry_units" : "m",
    "Service_wire_single_phase" : {
        "conductor_spacing" : 0.47,
        "num_of_cond" : 2,
        "num_of_phases" : 1, 
        "height_of_top_conductor": 8.0,
        "phase_conductor":"AAAC_4.0",
        "neutral_conductor" : "AAAC_4.0",
        "units": "m",
        "spacing": "vertical"
    },
    "Service_wire_three_phase": {
        "conductor_spacing" : 0.47,
        "num_of_cond" : 4,
        "num_of_phases" : 3, 
        "height_of_top_conductor": 8.0,
        "phase_conductor": "AAAC_4.0",
        "neutral_conductor" : "AAAC_4.0",
        "units": "m",
        "spacing": "vertical"
    },
    "ht_three_phase" : {
        "conductor_spacing" : 1.0,
        "num_of_cond" : 3,
        "num_of_phases" : 3,
        "height_of_top_conductor": 9.0,
        "phase_conductor": "RABBIT_7/3.35",
        "neutral_conductor" : "RABBIT_7/3.35",
        "units": "m",
        "spacing":"vertical"
    },
    "Consumer_kv": {
        "ht_consumer_ll" : 11.0,
        "ht_consumer_phase" : 6.6,
        "lt_consumer_ll" : 0.44,
        "lt_consumer_phase" : 0.23
    },
    "load_type": {
        "lt_consumer" : "wye",
        "ht_consumer" : "delta"
    },
    "ht_line": {
        "node_file_name" : "Asset_HT_Line_node.csv",
        "attribute_file_name" : "Asset_HT_Line_attribute.csv"
    },
    "ht_cable": {
        "node_file_name" : "Asset_HT_Line_Cable_node.csv",
        "attribute_file_name" : "Asset_HT_Line_Cable_attribute.csv"
    },
    "lt_line":{
        "node_file_name" : "Asset_LT_Line_node.csv",
        "attribute_file_name" : "Asset_LT_Line_attribute.csv"
    },
    "lt_cable":{
        "node_file_name" : "Asset_LT_Line_Cable_node.csv",
        "attribute_file_name" : "Asset_LT_Line_Cable_attribute.csv"
    },
    "line_column_mapper": {
        "length" : ["SHAPE_Leng"],
        "phase" :  ["force","RYB"],  
        "four_conductor_system" : ["3Ph Five wire system","3Ph Four wire system"],
        "three_conductor_system" : ["3Ph Three wire system"],
        "two_conductor_system" : ["1Ph Three wire system","1Ph Two wire system","2Ph Three wire system"],
        "phase_system" : ["HTL_PWS","HTLC_PWS","LTL_PWS","LTLC_PWS"],
        "csize" : ["HTL_CSIZE_","HTLC_CBL_S","LTL_CSIZE","LTLC_CBL_S"],
        "cname" : ["HTL_CNAME","HTLC_CBL_T","LTL_CNAME","LTLC_CBL_T"],
        "nsize" : ["LTL_N_CSIZ"],
        "nname" : ["LTL_N_CNAM"],
        "units" : ["force","m"],  
        "spacing" : ["force","vertical"]
    },
    "distribution_transformer":{"file_name" : "Asset_Distribution_Transformer.csv"},
    "power_transformer":{"file_name" : "Asset_Power_Transformer.csv"},
    "transformer_column_mapper": {
        "ID"  : ["DT_ID","PTR_ID"],
        "KVA_cap" : ["DT_CC_KVA","PTR_CAP_MV"],
        "HV_KV" : ["DT_HVSV_KV","PTR_PRY_VO"],
        "LV_KV" : ["DT_LVSV_KV","PTR_SEC_VO"],
        "maxtap" : ["force","1.1"],
        "mintap" : ["force","0.9"],
        "tap" : ["force","1.0"],
        "numtaps" : ["force","10"],
        "prim_con" : ["force","delta"],
        "sec_con" : ["force","wye"],
        "vector_group" : ["force","Dyn11"],
        "%resistance" : ["force","0.75"],
        "%reactance" : ["force","7.5"],
        "%noloadloss" : ["force","0"],
        "phase" : ["force","RYB"],
        "x" : ["x"],
        "y" : ["y"]
    },
    "lt_consumer": {"file_name" : "Consumer_LT.csv"},
    "ht_consumer":{"file_name" : "Consumer_HT.csv"},
    "consumer_column_mapper": {
        "pf" : ["LTC_PF","HTC_PF"],
        "tariff_type" : ["LTC_TCODE","HTC_TCODE"],
        "phase": ["LTC_PHASE","HTC_PHASE"],
        "Sanctioned_load" : ["LTC_SLOAD_","HTC_SDEMAN"],
        "x" : ["x"],
        "y" : ["y"],
        "PeakMWload" :  1.2,
        "estimate_consumer_peakkw" : "yes"
    },
    "consumer_class_by_tariff":{
        "residential" : ["LT Tariff IA","LT Tariff I B","LT Tariff VI"],
        "commercial" : ["LT Tariff II-A","LT Tariff II-B(1)","LT Tariff II-C", "LT Tariff V","LT Tariff II-B(2"],
        "industrial" : ["LT Tariff III-A (1)", "LT Tariff III-B","TARIFF III"],
        "agricultural" : ["LT Tariff IV"]
    },
    "peak_contribution": {
        "residential" : 0.867,
        "commercial" : 0.105,
        "industrial" : 0.017,
        "agricultural" : 0.011
    },
    "tec_per_kw_by_consumer_type":{
        "residential" : 5937.831,
        "commercial" : 6168.84,
        "industrial" : 6206.385,
        "agricultural" : 6102.5
    }
}

VALID_SETTINGS = {
    "project_path" : {'type':str},
    "feeder_name" : {'type':str},
    "log_settings": {
        "save_in_file": {'type':bool},
        "log_folder": {'type':str},
        "log_filename":{'type':str},
        "clear_old_log_file": {'type':bool}
        },
    "MVA_to_KVA_conversion_for_PT"  : {'type':str,'options':["yes","no"]},
    "force_lt_be_three_phase" : {'type':str,'options':["yes","no"]},
    "PTrow" :  {'type':int},
    "three_phase" : {'type':str},
    "single_phase" :{'type':list},
    "height_of_top_conductor_ht" : {'type': float},
    "height_of_top_conductor_lt" : {'type': float},
    "ht_spacing" : {'type': float},
    "lt_spacing" : {'type': float},
    "geomtry_units" : {'type':str,'options':["m"]},
    "Service_wire_single_phase" : {
        "conductor_spacing" : {'type': float},
        "num_of_cond" : {'type': int},
        "num_of_phases" : {'type': int}, 
        "height_of_top_conductor": {'type': float},
        "phase_conductor":{'type':str},
        "neutral_conductor" :{'type':str},
        "units": {'type':str,'options':["m"]},
        "spacing": {'type':str,'options':["vertical","horizontal"]}
    },
    "Service_wire_three_phase": {
        "conductor_spacing" : {'type': float},
        "num_of_cond" : {'type': int},
        "num_of_phases" : {'type': int}, 
        "height_of_top_conductor": {'type': float},
        "phase_conductor": {'type':str},
        "neutral_conductor" : {'type':str},
        "units": {'type':str,'options':["m"]},
        "spacing": {'type':str,'options':["vertical","horizontal"]}
    },
    "ht_three_phase" : {
        "conductor_spacing" : {'type': float},
        "num_of_cond" : {'type': int},
        "num_of_phases" : {'type': int},
        "height_of_top_conductor": {'type': float},
        "phase_conductor": {'type':str},
        "neutral_conductor" : {'type':str},
        "units": {'type':str,'options':["m"]},
        "spacing":{'type':str,'options':["vertical","horizontal"]}
    },
    "Consumer_kv": {
        "ht_consumer_ll" : {'type': float},
        "ht_consumer_phase" :{'type': float},
        "lt_consumer_ll" : {'type': float},
        "lt_consumer_phase" : {'type': float}
    },
    "load_type": {
        "lt_consumer" : {'type':str,'options':["wye","delta"]},
        "ht_consumer" : {'type':str,'options':["wye","delta"]}
    },
    "ht_line": {
        "node_file_name" : {'type':str},
        "attribute_file_name" : {'type':str}
    },
    "ht_cable": {
        "node_file_name" : {'type':str},
        "attribute_file_name" : {'type':str}
    },
    "lt_line":{
        "node_file_name" : {'type':str},
        "attribute_file_name" : {'type':str}
    },
    "lt_cable":{
        "node_file_name" : {'type':str},
        "attribute_file_name" : {'type':str}
    },
    "line_column_mapper": {
        "length" :{'type':list},
        "phase" :  {'type':list},  
        "four_conductor_system" : {'type':list},
        "three_conductor_system" : {'type':list},
        "two_conductor_system" : {'type':list},
        "phase_system" : {'type':list},
        "csize" : {'type':list},
        "cname" : {'type':list},
        "nsize" : {'type':list},
        "nname" : {'type':list},
        "units" : {'type':list},  
        "spacing" : {'type':list}
    },
    "distribution_transformer":{
        "file_name" : {'type':str}
    },
    "power_transformer":{
        "file_name" : {'type':str}
    },
    "transformer_column_mapper": {
        "ID"  : {'type':list},
        "KVA_cap" : {'type':list},
        "HV_KV" : {'type':list},
        "LV_KV" : {'type':list},
        "maxtap" : {'type':list},
        "mintap" : {'type':list},
        "tap" : {'type':list},
        "numtaps" : {'type':list},
        "prim_con" : {'type':list},
        "sec_con" : {'type':list},
        "vector_group" : {'type':list},
        "%resistance" : {'type':list},
        "%reactance" : {'type':list},
        "%noloadloss" : {'type':list},
        "phase" : {'type':list},
        "x" : {'type':list},
        "y" : {'type':list}
    },
    "lt_consumer": {"file_name" : {'type':str}},
    "ht_consumer":{"file_name" : {'type':str}},
    "consumer_column_mapper": {
        "pf" : {'type':list},
        "tariff_type" : {'type':list},
        "phase": {'type':list},
        "Sanctioned_load" : {'type':list},
        "x" : {'type':list},
        "y" : {'type':list},
        "PeakMWload" :  {'type': float},
        "estimate_consumer_peakkw" : {'type':str,'options':['yes','no']}
    },
    "consumer_class_by_tariff":{
        "residential" : {'type':list},
        "commercial" : {'type':list},
        "industrial" : {'type':list},
        "agricultural" : {'type':list}
    },
    "peak_contribution": {
        "residential" : {'type': float},
        "commercial" : {'type': float},
        "industrial" : {'type': float},
        "agricultural" : {'type': float}
    },
    "tec_per_kw_by_consumer_type":{
        "residential" : {'type': float},
        "commercial" : {'type': float},
        "industrial" : {'type': float},
        "agricultural" : {'type': float}
    }
}
