
""" Default values : DO NOT CHANGE !!!"""

LOG_FORMAT = "%(asctime)s:  %(levelname)s:  %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
MAXITERATIONS = 100
LIFE_PARAMETERS = {"theta_i":30,"theta_fl":36,"theta_gfl":28.6,
                    "R":4.87,"n":1,"tau":3.5,"m":1,"A":-13.391,
                    "B":6972.15,"num_of_iteration":4,}
DEFAULT_TEMP = 25
MAX_TRANS_LOADING = 1.5


DEFAULT_CONFIGURATION = {
    "dss_filepath": "",
    "dss_filename":"",
    "extra_data_path": ".",
    "export_folder":"",
    "start_time":"2018-1-1 0:0:0",
    "end_time":"2018-2-1 0:0:0",
    "simulation_time_step (minute)": 15,
    "frequency": 50,
    "upper_voltage": 1.1,
    "lower_voltage":0.9,
    "record_every": 96,
    "export_voltages": False,
    "export_lineloadings": False,
    "export_transloadings":False,
    "export_start_date": "",
    "export_end_date": "",
    "volt_var": {
                "enabled": False,
                "yarray": [0.44,0.44,0,0,-0.44,-0.44],
                "xarray": [0.7,0.90,0.95,1.05,1.10,1.3]
                },
    "log_settings": {
                    "save_in_file": False,
                    "log_folder": ".",
                    "log_filename":"logs.log",
                    "clear_old_log_file": True
                    }
}

DEFAULT_ADVANCED_CONFIGURATION = {
    "project_path": "C:\\Users\\KDUWADI\\Desktop\\NREL_Projects\\CIFF-TANGEDCO\\TANGEDCO\\EMERGE\\Projects",
    "active_project":"GR_PALAYAM",
	"active_scenario": "FullYear",
	"dss_filename":"gr_palayam.dss",
    "start_time":"2018-1-1 0:0:0",
    "end_time":"2018-1-2 0:0:0",
    "simulation_time_step (minute)": 60,
    "frequency": 50,
    "upper_voltage": 1.1,
    "lower_voltage":0.9,
    "record_every": 4,
    "parallel_simulation":True,
    "parallel_process": 1,
    "export_voltages": False,
    "export_lineloadings": False,
    "export_transloadings":False,
    "export_start_date": "",
    "export_end_date": "",
    "volt_var": {
                "enabled": True,
                "yarray": [0.44,0.44,0,0,-0.44,-0.44],
                "xarray": [0.7,0.90,0.95,1.05,1.10,1.3]
                },
    "log_settings": {
                    "save_in_file": False,
                    "log_filename":"",
                    "clear_old_log_file": True
                    }
}

VALID_SETTINGS = {
                "project_path":{'type':str},
                "active_project":{'type':str},
                "active_scenario":{'type':str},
                "dss_filepath": {'type': str},
                "dss_filename":{'type':str},
                "export_folder":{'type':str},
                "start_time":{'type':str},
                "end_time":{'type':str},
                "simulation_time_step (minute)":{'type':int},
                "frequency": {'type':int,'options':[50,60]},
                "upper_voltage": {'type':float,'range':[1,1.5]},
                "lower_voltage":{'type':float,'range':[0.8,1]},
                "record_every": {'type':int},
                "extra_data_path":{'type':str},
                "parallel_simulation":{'type':bool},
                "parallel_process": {'type':int,'range':[1,4]},
                "export_voltages": {'type':bool},
                "export_lineloadings": {'type':bool},
                "export_transloadings":{'type':bool},
                "export_start_date": {'type':str},
                "export_end_date": {'type':str},
                "volt_var": {
                            "enabled": {'type':bool},
                            "yarray": {'type':list},
                            "xarray": {'type':list}
                            },
                "log_settings": {
                                "save_in_file": {'type':bool},
                                "log_folder": {'type':str},
                                "log_filename":{'type':str},
                                "clear_old_log_file": {'type':bool}
                                }
            }


