# Standard modules
import logging

# External modules
import opendssdirect
import pandas as pd

# Internal modules
from dssmetrics.abstract_metrics import Metric


class SystemMetric(Metric):

    """ Class to compute system level metrics. Must inherit 'Metric' abstract class.
    """

    def __init__(self,dss_instance,config_dict,logger=None):
        super().__init__(dss_instance,config_dict,logger)

        self.metriclist = ["System"]
        self.initialize_result_containers(self.metriclist)
        
        for element in ["SARDI_voltage","SARDI_line","SARDI_transformer",
                        "SARDI_aggregated","SE","SE_line","SE_transformer","SOG","SATLOL"]:
            for metric in self.metriclist:
                self.metric[metric][element] = 0
                self.timeseries_metric[metric][element] = []

        
        # extra variables 
        self.totalloss, self.totalactivepower = 0,0
        self.previous_totalloss, self.previous_totalactivepower = 0,0
        self.lineloss, self.transloss = 0,0
        self.previous_lineloss, self.previous_transloss = 0,0
        self.total_loss_of_life,self.previous_lol = 0,0

        self.logger.info('SystemMetric class initiallized')
        

    def update(self,dss_instance,current_time,timeseries_record,
                    count,node_instance,line_instance,trans_instance):

        super().update(dss_instance,current_time,timeseries_record)

        node_customers = node_instance.get_customerslist()
        line_customers = line_instance.get_customerslist()
        trans_customers = trans_instance.get_customerslist()
        all_customers_impacted = list(set(node_customers).union(set(line_customers),set(trans_customers)))

        metric_dict = {"SARDI_voltage": node_customers,
                        "SARDI_line": line_customers,
                        "SARDI_transformer":trans_customers,
                        "SARDI_aggregated":all_customers_impacted}
        
        for metric, cutomers_list in metric_dict.items():
            self.metric['System'][metric] += (len(cutomers_list)/self.dss_instance.Loads.Count()) \
                            *self.config_dict["simulation_time_step (minute)"]*100/count

        
        self.totalloss += abs(self.dss_instance.Circuit.Losses()[0])
        self.totalactivepower += abs(self.dss_instance.Circuit.TotalPower()[0])

        self.metric['System']['SE'] = 100 - self.totalloss/(10*self.totalactivepower) \
                                if self.totalactivepower >0.01 else 100

        Linelosses, Translosses  = line_instance.get_losses(), trans_instance.get_losses()
        self.lineloss += Linelosses
        self.transloss += Translosses
        
        self.metric['System']['SE_line'] = 100 - self.lineloss/(10*self.totalactivepower) \
                                if self.totalactivepower >0.01 else 100
        
        self.metric['System']['SE_transformer'] = 100 - self.transloss/(10*self.totalactivepower) \
                                if self.totalactivepower >0.01 else 100

        circuit_power = self.dss_instance.Circuit.TotalPower()[0]
        self.metric['System']['SOG'] += circuit_power*self.config_dict["simulation_time_step (minute)"]/60 \
                                        if circuit_power>0 else 0

        self.total_loss_of_life += trans_instance.get_totallossoflife()
        self.metric['System']['SATLOL'] = self.total_loss_of_life/self.dss_instance.Transformers.Count()


        # update metric

        if timeseries_record:
            
            for metric in ["SARDI_voltage","SARDI_line","SARDI_transformer","SARDI_aggregated","SOG"]:
                previousvalue = self.metric['System'][metric] - sum(self.timeseries_metric['System'][metric])
                self.timeseries_metric['System'][metric].append(previousvalue)
            

            daily_loss = self.totalloss - self.previous_totalloss 
            daily_lineloss = self.lineloss - self.previous_lineloss
            daily_transloss = self.transloss - self.previous_transloss

            daily_power = self.totalactivepower - self.previous_totalactivepower

            daily_efficiency = 100 - daily_loss/(10*daily_power) if daily_power >0.01 else 100
            daily_lineefficiency = 100 - daily_lineloss/(10*daily_power) if daily_power >0.01 else 100
            daily_transefficiency = 100 - daily_transloss/(10*daily_power) if daily_power >0.01 else 100

            self.timeseries_metric['System']['SE'].append(daily_efficiency)
            self.timeseries_metric['System']['SE_line'].append(daily_lineefficiency)
            self.timeseries_metric['System']['SE_transformer'].append(daily_transefficiency)

            self.previous_totalloss = self.totalloss
            self.previous_totalactivepower = self.totalactivepower
            self.previous_lineloss = self.lineloss
            self.previous_transloss = self.transloss

            daily_lossoflife = self.total_loss_of_life - self.previous_lol
            self.timeseries_metric['System']['SATLOL'].append(daily_lossoflife \
                                        /self.dss_instance.Transformers.Count())
            self.previous_lol = self.total_loss_of_life