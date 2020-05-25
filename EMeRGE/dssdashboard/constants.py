
FOLDER_LIST = ['Coordinates','PVMetrics','AdvancedPVMetrics','Profile','PVConnection']

LOG_FORMAT = "%(asctime)s:  %(levelname)s:  %(message)s"

TABLIST = ["Initial Assessment","PV Connection Request","Classical PV","Advanced PV","EV"]

HEADER_TITLE = " Distribution System Analysis Dashboard"

HEADER_DETAIL = "Framework to visualize system level and asset level metrics to inform decision making."

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

DEFAULT_CONFIGURATION = {
    "project_path": "",
    "active_project":"",
    "time_step(min)":15,
    "year": 2018,
    "log_filename":"",
    "pv_connection": {
        "dss_filename": "",
        "simulation_time_step (minute)": 15,
        "frequency": 50,
        "upper_voltage": 1.1,
        "lower_voltage":0.9
    }
}

VALID_SETTINGS = {
                "project_path":{'type':str},
                "active_project":{'type':str},
                "time_step(min)":{'type':int},
                "year": {'type':int},
                "log_filename":{'type':str},
                "pv_connection": {
                        "dss_filename": {'type':str},
                        "simulation_time_step (minute)": {'type':int},
                        "frequency": {'type':int,'options':[50,60]},
                        "upper_voltage": {'type':float,'range':[1,1.5]},
                        "lower_voltage":{'type':float,'range':[0.8,1]}
                    }
}

PROFILE_TEXTS = {
    'first_layer': {
        'heading': "Initial Load Profile Analysis: Effect of PV on load profile and important statistics",
        'detail': " Utility often want to know the shape of load profile. Increasing PV penetration affects these load shapes. This tool " \
                    "allows utility to see load profile for different consumer class and also see how the load shape changes" \
                    " when PV penetration increases. Note the PV penetration in this tool is defined based on percentage" \
                    " of peak load of the feeder and is not same as PV scenario defined in other tabs. Also it does take " \
                    "into account the location where they are installed. "
    }, 
}

METRIC_TEXTS = {
    "first_layer": {
        'heading': "System Level Risk Metrics",
        'detail': "Percentage time average customer would experience violations are defined as risk metrics. Violations are" \
                    "categorized into three types: Voltage violation (any voltage magnitude above 1.1 pu and below 0.9 pu)" \
                    " , line violation (loading aboove 100%) and transformer violation (above 100%). SARDI_voltage, SARDI_line," \
                    "SARDI_transformer represent System Average Risk Duration Index for voltage, line and transformer violation" \
                    " respectievely. SARDI_aggregated represents System Average Risk Duration Index for all violations. Knowing" \
                    "how PV deployement would alter these risk metrics can better inform PV deployement decisions. Base case means"  
                    "no PV. PV scenarios is defined by two components. For e.g. 10%-100% PV scenario means that 10% of "
                    "total customers (chosen uniformly randomly) have installed PV with a capcity to meet 100% of their annual "\
                    "energy need when they do not have PV in their system."
                },
   "second_layer" :  {
       'heading': "Percentage Energy Loss",
       'detail': "Percentage energy Loss is an indicator of efficiency. Loss in the energy is a loss in economic"
                "reveune and also increases loss of life of an equipment (such as conductors and transformers)." \
                " Along with risk metrics we also need to see how PV deployment affects percentage energy loss." \
                "Higher deployement of PV would increase loading in the distribution network thus increasing loss in the system. " \
                "SE_line, SE_transformer and SE represent system energy loss for line elements (including both" 
                "conductors and cables), system energy loss for transformers and overall system energy loss." 
                "Accuracy of these results depend on accuracy of parameters of component such as resistance," \
                "reactance, capacitance, percentage loss during full load and no load of transformer etc." 
                "Furthermore, how accurate load profiles are also has an impact. Field measurements could" \
                "certainly help validating these results."
            },
    "third_layer" : {
        'heading': "Percentage Loss of Life of Transformer",
        'detail' : "Transformer loss of life is a function of hot-spot temperature inside transformer element. Hot spot" \
                  "temperature further depends on loading pattern which certainly would be affected by PV deployment." \
                    " IEEE C57.92-1981 provides detail description on how to compute loss of life from loading pattern."  
                    "Here we have assumed life of transformer is determined by deterioration of insulating material because of" \
                    " temperature. The numbers are reliable only if the loadings are normal (meaning not severly high for" 
                    "long period of time). This may not be highly accurate now however provides relative understanding pattern" 
                    "in loss of life because of PV deployement providing more support to PV deployement decision."
    },
    "fourth_layer":{
        'heading':"Percentage Overgeneration by PV",
        'detail': "Higher deployment of PV can cause reverse power flow in the system which can accumulate at the"
                  "substation level. If there is a limit on reverse power flow because of storage constraints or market" \
                  "constraints or any other constraints deploying PV above certain percentage of overgeneration might" \
                   "be infesabile to utility. This metric further complements the PV deployement decesion by providing" \
                  "more insight on PV overgeneration. For now we have not included storage in the system. Furthermore," \
                   "more advanced protection scheme might be necessary to allow reverse power flow in the system."
    },
    "fifth_layer": {
        'heading': "Time Series System Level Metrics: Understading daily variation of system level risk metrics",
        'detail': "Now let's take a look at above metrics in time-series mode. How would above metrics vary in time" \
                "at different PV scenarios would help us identify day when they are highly impacted. You can select" \
                "PV scenarios and observe metric variation in the graph. Note you can multi-select parameters" \
                "to observe. Values are aggregated for day."
    },
    "sixth_layer": {
        'heading': "Time Series Asset Level Metric: Scatter plot on top of network map",
        'detail' : "Now that we know what the system level distribution metric look like, it is also important to know"  
                    "which asset are at vulnerable state or which asset is actually causing problem. The Scatter plot"\
                    "on top of network allows utility which components are vulnerable and where they are located and at" \
                    "what time. User can use dropdown menu to select different PV scenarios."
    },
    "seventh_layer": {
        'heading': "Asset Level Metric: Table and Aggregated Map",
        'detail': " The aggreagted metric for an asset is listed in table on the right and shown in the form of scatter" \
                  "heatmap on the left. Size and color both help to identify vulnerable component. The components are" \
                 "selected based on the metric you selected to observe in time series asset level metric."
    }
}

PVCONNECTION_TEXTS = {
    'first_layer': {
        'first_col': {
            'heading': "Input for New PV Request",
            'detail': "User should input valid data for all the fields below." 
                    "Please zoom in on the network shown on the right and " \
                    " hover over the node to see the name of the node where PV connection is requested."
        },
        'second_col':{
            'heading': "PV analysis time period ",
            'detail': "Perform 24 hour power flow on the backend and compares the result with base case. "
        },
        'third_col':{
            'heading': "Network to add PV",
            'detail': "Zoom in the network and hover over to see the name of node where you want to add PV."
        }
    },
    'second_layer':{
        'heading': "PV Connection Request : Control Panel",
        'detail': " Before accepting PV connection request, utility might need to perform initial assessment of" 
                "whether such PV connection might affect the grid in an adverse manner or not." \
                " This tool is exactly for that. When consumer submits PV connection request utiliy can input " \
                "the parameter here and will show impact on different distribution metrics which helps utility to " \
                              "accept or reject the request."
    },
    'third_layer':{
        'first_col': {
            'heading': "Voltage profile (Base)",
            'detail': " The plot below shows voltage heatmap on top of network \
                        for last time stamp of the simulation."
        },
        'second_col':{
            'heading': "Line loading heatmap (Base)",
            'detail':  " The plot below shows a line loading heatmap on top of network for last time stamp \
            of the simulation."
        },
        'third_col':{
            "heading": "Transformer loading heatmap (Base)",
            "detail": " The plot below shows a transformer loading heatmap on top of network \
            for last time stamp of the simulation."
        }

    },
    'fourth_layer':{
        'first_col': {
            'heading': "Voltage profile",
            'detail': " The plot below shows voltage heatmap on top of network \
            for last time stamp of the simulation."
        },
        'second_col':{
            'heading': "Line loading heatmap",
            'detail': " The plot below shows a line loading heatmap on top of network \
            for last time stamp of the simulation."
        },
        'third_col':{
            'heading': "Transformer loading heatmap",
            'detail': " The plot below shows a transformer loading heatmap on top of \
            network for last time stamp of the simulation."
        }

    }
}