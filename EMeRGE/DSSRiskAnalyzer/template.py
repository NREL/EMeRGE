class TomlDictForDSSRiskAnalyzer:

    def __init__(self):

        self.toml_dict = {
            "Project path" : "C:\\Users\\KDUWADI\\Desktop\\NREL_Projects\\CIFF-TANGEDCO\\TANGEDCO\\SoftwareTools\\Distribution_Metric_Computing_Tool\\Projects",
            "Active_Feeder" : "GWC",
            "Active_Scenario" : "Category_Apr",
            "DSSfilename" : 'gwc.dss',
            "voltage_upper_limit" : 1.1,
            "voltage_lower_limit" : 0.9,
            "line_loading_upper_limit" : 1.0,
            "transformer_loading_upper_limit" : 1.0,
            "simulation_time_step" : 15,
            "simulation_time_unit" : 'Minute',
            "start_time" : "2018/04/01 00:00:00",
            "stop_time" : "2018/05/01 00:15:00",
            "time_format" : '%Y/%m/%d %H:%M:%S',
            "Risk_metric_aggregate_minutes" : 1440,
            "Maximum_Iteration" : 100,
            "FileNames":{
                "TransformerDownwardCustomers" : 'transformer_cust_down.p',
                "LineDownwardCustomers" : 'line_cust_down.p',
                "NodeDownwardCustomers" : 'node_cust_down.p',
                "TransformerLifeParameters" : 'transformer_life_parameters.csv',
                "TemperatureData" : 'temp_data_15min.csv',
            },
        }

    def ReturnDict(self):
        return self.toml_dict
