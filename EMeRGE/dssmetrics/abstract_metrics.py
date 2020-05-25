""" Abstract class for computing metrics
"""
# standard modules
from abc import ABC, abstractmethod
import logging
import os

# External libraries
import pandas as pd

# internal modules
from dssmetrics.constants import LOG_FORMAT

class Metric:

    """
    Abstract class for computing metrics using results of
    time-series OpenDSS power flow.
    """

    def __init__(self, dss_instance: object,config_dict: dict, logger: object):

        """ Constructor for Metric Abstract class."""

        self.dss_instance = dss_instance
        self.config_dict = config_dict
        if logger == None:
            self.logger = logging.getLogger()
            logging.basicConfig(format=LOG_FORMAT,level='DEBUG')
        else:
            self.logger = logger

    @abstractmethod
    def update(self,dss_instance:object ,current_time: object,timeseries_record:bool):

        """ Default update method for class which inherits 'Metric' abstract class. """

        self.dss_instance = dss_instance

        # update time_stamps if record flag is on
        if timeseries_record:
            self.timestamps.append(current_time)

        # initiallize some variables 
        self.reinitialize()


    def initialize_result_containers(self, metriclist: list):

        """Initiallize containers to store results"""

        self.metric = {metric:{} for metric in metriclist}
        self.timeseries_metric = {metric:{} for metric in metriclist}
        self.gamma = {}
        self.customers_impacted = []
        self.timestamps = []
        self.logger.info('initialized result containers')  

    def get_gamma(self):
        
        """ returns gamma variable: depth of violation"""
        return self.gamma 

    def get_customerslist(self):

        """ returns list of customers impacted by violation"""
        return self.customers_impacted    

    def reinitialize(self):

        """ re-initiallize at the begining of each update"""

        for load_name in self.dss_instance.Loads.AllNames():
            self.gamma[load_name] = 0 
        self.customers_impacted = [] 
        self.losses = 0   

    def exportAPI(self, exportpath: str = '.'):

        """ Top level API to export metrics"""

        # add time-stamps to time_series metrics
        for keys in self.timeseries_metric.keys():
            self.timeseries_metric[keys]['TimeStamps'] = self.timestamps

        # export all metrics
        self.export(self.metric, exportpath=exportpath)
        self.export(self.timeseries_metric,exportpath=exportpath, index='TimeStamps')


    def export(self, metric_dict: dict, exportpath: str ='.', index: str ='') -> str:

        " Lower level method to export metrics "

        for keys, subdict in metric_dict.items():

            if not isinstance(subdict,dict):
                raise TypeError(f'{subdict} is not of type {dict}')
            
            assert (os.path.exists(exportpath)),f"{exportpath} does not exist!"

            
            if any(isinstance(values,(float,int)) for values in subdict.values()):
                df = pd.DataFrame({
                    'component_name': list(subdict.keys()),
                    'values': list(subdict.values())
                })
                filename = keys + '.csv'
                
            
            elif any(isinstance(values,list) for values in subdict.values()):
                df = pd.DataFrame(subdict)
                if index in df.columns:
                    df = df.set_index(index)
                elif index !='':
                    self.logger.warning(f'{index} does not exists, FAILED to index dataframe...')
                     
                filename = keys + '_timeseries.csv'
            
            else:
                raise TypeError(f'Values neither {float,int} nor {list}')

            df.to_csv(os.path.join(exportpath,filename))
            self.logger.info(f"{os.path.join(exportpath,filename)} successfully exported.")
            
            
        return "success"

