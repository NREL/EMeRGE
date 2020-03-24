class TomlDictForCSV2DSS:

    def __init__(self):

        self.toml_dict = {
            "Project path" : "C:\\Users\\KDUWADI\\Desktop\\NREL_Projects\\CIFF-TANGEDCO\\TANGEDCO\\SoftwareTools\\Standard_CSVs_to_DSS_files",
            "Feeder name" : "GWC",
            "PV_customers_step" : 10,
            "PV_capacity_step" : 1,
            "number_of_monte_carlo_run" : 1,
            "export_pickle_for_risk_analysis" : "yes",
            "time_series_pf" : "yes",
            "num_of_data_points" : 35040,
            "minute-interval" : 15,
            "time_series_voltage_profile" : "yes",
            "voltage_csv_name" : "voltagemult.csv",
            "sourcebasekv" : 33,
            "sourcebasefreq" : 50,
            "sourcepu" : 1.0,
            "sourcezeroseq_impedance" : [0.001,0.001],
            "sourceposseq_impedance" : [0.001,0.001],
            "source_num_of_phase" : 3,
            "include_PV" : "yes",
            "PV_volt_label" : [0.44,0.23],
            "annual_PV_capacity_factor" : 0.25,
            "inverter_oversize_factor" : 0.9,
            "max_pu_irradiance" : 0.98,
            "no_reactive_support_from_PV" : "yes",
            "PV_cutin" : 0.05,
            "PV_cutout" : 0.05,
            "solar_csvname" : 'solarmult.csv',
            "three_phase" : "RYB",
            "single_phase" : ["R","Y","B"],
            "random_phase_allocation" : "yes",
            "multi_threephase_for_lt" : "yes",
            "num_of_parallel_three_phase" : 3,
            "servicewire_phase_conductor_type" : "AAAC",
            "servicewire_phase_conductor_size" : "4.0",
            "phase_conductor_type_ht_consumer" : "RABBIT",
            "phase_conductor_size_ht_consumer" : "7/3.35",
            "service_wire_spacing" : "vertical",
            "ht_consumer_conductor_spacing" : "vertical",
            "units_for_coordinate" : 'm',
            "service_wire_num_of_cond" : {
                "single_phase" : 2,
                "three_phase" : 4
            },
            "ht_consumer_conductor_num_of_cond": {"three_phase" : 3},
            "phase2num" :{"R" : 1,"Y" : 2,"B" : 3},

        }

    
    def ReturnDict(self):

        return self.toml_dict