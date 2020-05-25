# Standard modules
import logging

# External modules
import opendssdirect
import pandas as pd

# Internal modules
from dssmetrics.abstract_metrics import Metric


class CustomerMetric(Metric):

    """ Class to compute metrics realated to customers in the distriution
    feeder. Must inherit 'Metric' abstract class.
    CRI - Nodal voltage risk duration index (% of simulation-time node experiences voltage violation
    weighted by depth of violation.)
    """

    def __init__(self,dss_instance,config_dict,logger=None):
        super().__init__(dss_instance,config_dict,logger)

        self.metriclist = ["CRI"]
        self.initialize_result_containers(self.metriclist)
        
        for element in self.dss_instance.Loads.AllNames():
            for metric in self.metriclist:
                self.metric[metric][element] = 0
                self.timeseries_metric[metric][element] = []

        self.logger.info('CustomerMetric class initiallized')
        

    def update(self,dss_instance,current_time,timeseries_record,
                    count,node_instance,line_instance,trans_instance):

        super().update(dss_instance,current_time,timeseries_record)

        node_gamma = node_instance.get_gamma()
        line_gamma = line_instance.get_gamma()
        trans_gamma = trans_instance.get_gamma()

        # update metric
        self.dss_instance.Circuit.SetActiveClass('Load')
        flag = self.dss_instance.Loads.First()

        while flag>0:
            
            load_name = self.dss_instance.Loads.Name()

            cri_metric = (node_gamma[load_name] + line_gamma[load_name] + trans_gamma[load_name])/count

            self.metric['CRI'][load_name] += cri_metric

            if timeseries_record:
                
                previousvalue = self.metric['CRI'][load_name] - sum(self.timeseries_metric['CRI'][load_name])
                self.timeseries_metric['CRI'][load_name].append(previousvalue)

            flag = self.dss_instance.Loads.Next()

    
