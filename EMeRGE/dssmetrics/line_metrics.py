# Standard modules
import logging
import math
import os
from datetime import datetime as dt

# External modules
import opendssdirect
import pandas as pd
import pickle

# Internal modules
from dssmetrics.abstract_metrics import Metric
from dssmetrics.constants import DATE_FORMAT


class LineMetric(Metric):

    """ Class to compute metrics related to line elements in distribution network
    Metrics implemeted:
    1) LLRI - line loading risk index
    2) LE - line efficiency
    """

    def __init__(self,dss_instance,config_dict,logger=None):

        """ Constructor for LineMetric Class"""

        super().__init__(dss_instance,config_dict,logger)

        self.metriclist = ["LLRI","LE"]
        self.initialize_result_containers(self.metriclist)

        # Few other variables for stroing lossed and powers
        self.active_losses,self.pre_act_losses = {}, {}
        self.active_power, self.pre_act_power = {}, {}

        self.lineloading = {'TimeStamps':[]}
        
        for element in self.dss_instance.Lines.AllNames():
            for metric in self.metriclist:
                self.metric[metric][element] = 0
                self.timeseries_metric[metric][element] = []
                self.lineloading[element] = []

            self.active_losses[element] = 0
            self.active_power[element] = 0
            self.pre_act_losses[element] = 0
            self.pre_act_power[element] = 0

        self.read_files()

        # Check if line loading needs to be exported or not
        if self.config_dict['export_lineloadings']:
            self.export_start_time = dt.strptime(self.config_dict['export_start_date'],DATE_FORMAT)
            self.export_end_time = dt.strptime(self.config_dict['export_end_date'],DATE_FORMAT)

        self.logger.info('LineMetric class initiallized')

    def exportAPI(self, exportpath: str = '.'):
        
        super().exportAPI(exportpath=exportpath)

        if self.config_dict['export_lineloadings']:
            line_dataframe = pd.DataFrame(self.lineloading)
            line_dataframe = line_dataframe.set_index('TimeStamps')
            line_dataframe.to_csv(os.path.join(exportpath,'lineloading.csv'))
            self.logger.info('Line loadings exported successfully')

    def read_files(self):

        """ Read pickle file containing information on customers present
        downward of a node.
        """
        if 'line_cust_down.p' not in os.listdir(self.config_dict['extra_data_path']):
            raise Exception("'line_cust_down.p' does not exist!!")

        with open(os.path.join(self.config_dict['extra_data_path'],'line_cust_down.p'),"rb") as picklefile:
            self.line_cust_down = pickle.load(picklefile)

    def get_losses(self):

        """ return total line losses : updates every time stamps"""
        return self.losses
        

    def update(self,dss_instance,current_time,timeseries_record,count):

        """ update method (must be present)"""

        super().update(dss_instance,current_time,timeseries_record)

        if self.config_dict['export_lineloadings']:
            if self.export_start_time <= current_time <= self.export_end_time:
                self.lineloading['TimeStamps'].append(current_time)

        # loop through all line elements
        self.dss_instance.Circuit.SetActiveClass('Line')
        flag = self.dss_instance.Lines.First()

        while flag>0:
           
            line_name = self.dss_instance.Lines.Name()
            linecomplexcurrent = self.dss_instance.CktElement.Currents()
            line_current_limit = self.dss_instance.CktElement.NormalAmps()
            linecurrent = [math.sqrt(i ** 2 + j ** 2) for i, j in \
                                zip(linecomplexcurrent[::2], linecomplexcurrent[1::2])]
            loading = max(linecurrent)/line_current_limit

            # Compute for efficiency
            self.active_losses[line_name] += self.dss_instance.CktElement.Losses()[0]

            # will store losses from all line elements
            self.losses += self.dss_instance.CktElement.Losses()[0]
        
            complex_power = self.dss_instance.CktElement.Powers()
            frombuspower, tobuspower = sum(complex_power[:int(.5*len(complex_power)):2]), \
                                        sum(complex_power[int(.5*len(complex_power))::2])

            self.active_power[line_name] += max(abs(frombuspower),abs(tobuspower))

            efficiency = 100 - self.active_losses[line_name]/(10*self.active_power[line_name]) if \
                            self.active_power[line_name]>0.01 else 100
            
            self.metric['LE'][line_name] = efficiency
            
            # Compute for LLRI

            gamma = loading - 1 if loading>1 else 0
            #self.gamma[line_name] = gamma
            self.metric['LLRI'][line_name] += (len(self.line_cust_down[line_name]) \
                                            /self.dss_instance.Loads.Count())*gamma \
                                        *self.config_dict["simulation_time_step (minute)"]*100/count
            
            # updates impacted customers list if violation occurs
            if gamma > 0:
                self.customers_impacted = list(set(self.customers_impacted).union(set(self.line_cust_down[line_name])))
            
            # updates gamma for customers (depth of  violation)
            for load_name in self.line_cust_down[line_name]:
                if self.gamma[load_name] < gamma:
                    self.gamma[load_name] = gamma
            
            # Export line loadings
            if self.config_dict['export_lineloadings']:
                if self.export_start_time <= current_time <= self.export_end_time:
                    self.lineloading[line_name].append(loading)

            if timeseries_record:

                # update time-series line efficiency
                loss_daily = self.active_losses[line_name] - self.pre_act_losses[line_name]
                power_daily = self.active_power[line_name] - self.pre_act_power[line_name]
                efficiency_daily = 100 - loss_daily/(10*power_daily) if power_daily>0.01 else 100
                self.timeseries_metric['LE'][line_name].append(efficiency_daily)
                self.pre_act_losses[line_name] = self.active_losses[line_name]
                self.pre_act_power[line_name] = self.active_power[line_name]

                # update time-series LLRI
                previousvalue = self.metric['LLRI'][line_name] - sum(self.timeseries_metric['LLRI'][line_name])
                self.timeseries_metric['LLRI'][line_name].append(previousvalue)
            
            flag = self.dss_instance.Lines.Next()