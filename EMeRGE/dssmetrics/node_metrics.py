# Standard libraries
import logging
import os
import pickle
from datetime import datetime as dt

# External libraries
import opendssdirect
import pandas as pd

# Internal libraries
from dssmetrics.abstract_metrics import Metric
from dssmetrics.constants import DATE_FORMAT


class NodeMetric(Metric):

    """ Class to compute metrics realated to nodes in the distriution
    feeder. Must inherit 'Metric' abstract class.
    
    1) NVRI - Nodal voltage risk duration index (% of simulation-time node experiences voltage violation
    weighted by depth of violation.)
    """

    def __init__(self,dss_instance,config_dict,logger=None):

        """ Constructor for NodeMetric Class """

        super().__init__(dss_instance,config_dict,logger)

        self.metriclist = ["NVRI"]
        self.initialize_result_containers(self.metriclist)
        self.voltages = {'TimeStamps':[]}
        
        for element in self.dss_instance.Circuit.AllBusNames():
            for metric in self.metriclist:
                self.metric[metric][element] = 0
                self.timeseries_metric[metric][element] = []
                self.voltages[element] = []

        # read files required
        self.read_files()

        self.logger.info('NodeMetric class initiallized')

        # Check if voltage needs to be exported or not
        if self.config_dict['export_voltages']:
            self.export_start_time = dt.strptime(self.config_dict['export_start_date'],DATE_FORMAT)
            self.export_end_time = dt.strptime(self.config_dict['export_end_date'],DATE_FORMAT)
        
    
    def read_files(self):

        """ Read pickle file containing information on customers present
        downward of a node.
        """

        if 'node_cust_down.p' not in os.listdir(self.config_dict['extra_data_path']):
            raise Exception("'node_cust_down.p' does not exist!!")

        with open(os.path.join(self.config_dict['extra_data_path'],'node_cust_down.p'),"rb") as picklefile:
            self.node_cust_down = pickle.load(picklefile)

    def exportAPI(self, exportpath: str = '.'):
        
        super().exportAPI(exportpath=exportpath)

        if self.config_dict['export_voltages']:
            voltage_dataframe = pd.DataFrame(self.voltages)
            voltage_dataframe = voltage_dataframe.set_index('TimeStamps')
            voltage_dataframe.to_csv(os.path.join(exportpath,'voltages.csv'))
            self.logger.info('Voltage exported successfully')


    def update(self,dss_instance,current_time,timeseries_record,count):

        """ update method (must be present)"""

        super().update(dss_instance,current_time,timeseries_record)

        if self.config_dict['export_voltages']:
            if self.export_start_time <= current_time <= self.export_end_time:
                self.voltages['TimeStamps'].append(current_time)

        # loop through all the nodes in the network
        for busname in self.dss_instance.Circuit.AllBusNames():
            
            # activate the bus for measurement
            self.dss_instance.Circuit.SetActiveBus(busname)

            voltagelist = self.dss_instance.Bus.puVmagAngle()[::2]

            [maxVoltage,minVoltage] = [max(voltagelist),min(voltagelist)] \
                        if isinstance(voltagelist,list) else [voltagelist,voltagelist]

            # compute the NVRI metric for bus
            if maxVoltage < self.config_dict["upper_voltage"] and minVoltage > self.config_dict["lower_voltage"]: 
                gamma = 0
            
            if maxVoltage > self.config_dict["upper_voltage"] and minVoltage < self.config_dict["lower_voltage"]: 
                gamma = max([maxVoltage-self.config_dict["upper_voltage"],
                            self.config_dict["lower_voltage"]-minVoltage])
            
            if maxVoltage > self.config_dict["upper_voltage"] and minVoltage > self.config_dict["lower_voltage"]: 
                gamma = maxVoltage - self.config_dict["upper_voltage"]
            
            if maxVoltage < self.config_dict["upper_voltage"] and minVoltage < self.config_dict["lower_voltage"]: 
                gamma = self.config_dict["lower_voltage"] - minVoltage
            
            #self.gamma[busname] = gamma

            self.metric['NVRI'][busname] += (len(self.node_cust_down[busname]) \
                                            /self.dss_instance.Loads.Count())*gamma \
                                        *self.config_dict["simulation_time_step (minute)"]*100/count

            # update impacted customers list if violation occurs
            if gamma > 0:
                self.customers_impacted = list(set(self.customers_impacted).union(set(self.node_cust_down[busname])))

            # update the gamma for customers
            for load_name in self.node_cust_down[busname]:
                if self.gamma[load_name] < gamma:
                    self.gamma[load_name] = gamma 

            # Export voltages 
            if self.config_dict['export_voltages']:
                if self.export_start_time <= current_time <= self.export_end_time:
                    self.voltages[busname].append(sum(voltagelist)/len(voltagelist))
            
            if timeseries_record:
                
                previousvalue = self.metric['NVRI'][busname] - sum(self.timeseries_metric['NVRI'][busname])
                self.timeseries_metric['NVRI'][busname].append(previousvalue)

    
