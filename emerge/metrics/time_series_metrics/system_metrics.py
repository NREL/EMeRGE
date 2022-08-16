""" Module for managing computation of system level metrics. """

import opendssdirect as dss

from emerge.metrics.time_series_metrics import observer
from emerge.metrics import powerflow_metrics_opendss
from emerge.utils import dss_util

class SARDI_voltage(observer.MetricObserver):
    """ Class for managing the computation of SARDI voltage metric.
    
    Attributes:
        upper_threshold (float): Voltage upper threshold
        lower_threshold (float): Voltage lower threshold
        sardi_voltage (float): SARDI voltage metric
        counter (int): Counter for keeping track how number
            of times compute function is called
    """

    def __init__(
        self,
        upper_threshold: float = 1.05,
        lower_threshold: float = 0.95
    ):
        """ Constructor for SARDI_voltage metric.
        
        Args:
            upper_threshold (float): Voltage upper threshold
            lower_threshold (float): Voltage lower threshold
        """
        
        self.upper = upper_threshold
        self.lower = lower_threshold
        self.sardi_voltage = 0
        self.counter = 0

    def compute(self, dss_instance:dss):
        """ Refer to base class for more details. """

        # Get voltage dataframe and load bus mapper
        voltage_df = powerflow_metrics_opendss.get_voltage_dataframe(dss_instance)
        load_bus_map = dss_util.get_bus_load_dataframe(dss_instance)
        
        # Filter voltages for load buses only 
        # and count the number of overvoltages and undervoltages
        v_filter = voltage_df.loc[load_bus_map["busname"]].drop_duplicates()
        overvoltage_count = v_filter[v_filter['voltage(pu)']>self.upper].count()['voltage(pu)']
        undervoltage_count = v_filter[v_filter['voltage(pu)']<self.lower].count()['voltage(pu)']

        self.sardi_voltage += (overvoltage_count + undervoltage_count)*100/len(load_bus_map)
        self.counter +=1

    def get_metric(self):
        """ Refer to base class for more details. """
        return {
            "sardi_voltage": self.sardi_voltage/self.counter if self.counter >0 else 0
        }


