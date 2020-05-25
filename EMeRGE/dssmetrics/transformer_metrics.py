# Standard modules
import logging
import math
import os
import calendar
from datetime import datetime as dt
from datetime import timedelta

# External modules
import opendssdirect
import pandas as pd
import pickle

# Internal modules
from dssmetrics.abstract_metrics import Metric
from dssmetrics.constants import LIFE_PARAMETERS, DEFAULT_TEMP, MAX_TRANS_LOADING, DATE_FORMAT


class TransformerMetric(Metric):

    """ Class to compute metrics related to transformers
    1) TLRI (Transformer Loading Risk Index)
    2) TE (Transformer Efficiency)
    3) TOG (Transformer Overgeneration)
    4) TLOL (Transformer Loss of Life)
    """

    def __init__(self,dss_instance,config_dict,logger=None,year=2018):

        """ Constructor for TransformerMetric class"""

        super().__init__(dss_instance,config_dict,logger)

        self.metriclist = ["TLRI","TE","TOG", "TLOL"]
        self.initialize_result_containers(self.metriclist)

        # Few other variables
        self.active_losses,self.pre_act_losses = {}, {}
        self.active_power, self.pre_act_power = {}, {}
        self.totallol = 0
        self.transloading = {'TimeStamps':[]}
        
        for element in self.dss_instance.Transformers.AllNames():

            for metric in self.metriclist:
                self.metric[metric][element] = 0
                self.timeseries_metric[metric][element] = []
                self.transloading[element] = []

            self.active_losses[element] = 0
            self.active_power[element] = 0
            self.pre_act_losses[element] = 0
            self.pre_act_power[element] = 0

        # Read necessary file
        self.read_files(year)

        # Check if line loading needs to be exported or not
        if self.config_dict['export_transloadings']:
            self.export_start_time = dt.strptime(self.config_dict['export_start_date'],DATE_FORMAT)
            self.export_end_time = dt.strptime(self.config_dict['export_end_date'],DATE_FORMAT)

        self.logger.info('TransformerMetric class initiallized')
    
    def exportAPI(self, exportpath: str = '.'):
        
        super().exportAPI(exportpath=exportpath)

        if self.config_dict['export_transloadings']:
            trans_dataframe = pd.DataFrame(self.transloading)
            trans_dataframe = trans_dataframe.set_index('TimeStamps')
            trans_dataframe.to_csv(os.path.join(exportpath,'transloading.csv'))
            self.logger.info('Transformer loadings exported successfully')

    
    def read_files(self,year):

        # read pickle file
        
        with open(os.path.join(self.config_dict['extra_data_path'], \
            'transformer_cust_down.p'),"rb") as pickle_file:
            self.transformer_cust_down = pickle.load(pickle_file)
        
        # default temperature data

        num_of_days = 366 if calendar.isleap(year) else 365
        data_length_for_year = int(num_of_days*24*60/self.config_dict['simulation_time_step (minute)'])
        self.temperature_data = pd.DataFrame({
            'Temperature':[DEFAULT_TEMP]*data_length_for_year,
            'TimeStamps':[dt(year,1,1,0,0,0)+timedelta(minutes
                                    = self.config_dict['simulation_time_step (minute)'])*i \
                                    for i in range(data_length_for_year)]
        })
        self.temperature_data = self.temperature_data.set_index('TimeStamps')
        
        # read external temperature data
        if "temp_data_15min.csv" not in os.listdir(self.config_dict["extra_data_path"]):
            self.logger.warning(f"Unable to find 'temp_data_15min.csv' file, \
            forcing ambient temperature to be {DEFAULT_TEMP} degree at all times.")
            
        else:
            temp_dataframe = pd.read_csv(os.path.join(self.config_dict["extra_data_path"],\
                                        "temp_data_15min.csv"))
            if 'Temperature' not in self.temperature_data.columns:
                self.logger.warning(f"Temperature column does not exists in 'temp_data_15min.csv' \
                    forcing temperature to default {DEFAULT_TEMP} degree.")
            elif len(self.temperature_data) > len(temp_dataframe):
                self.logger.warning(f"Length of data in 'temp_data_15min.csv' is lesser for \
                            {self.config_dict['simulation_time_step (minute)']} minute resolution \
                                forcing default tempearture {DEFAULT_TEMP}")
            else:
                self.temperature_data['Temperature'] = temp_dataframe['Temperature'].tolist()\
                                                            [:len(self.temperature_data)]
                self.logger.info('Sucessfully read "temp_data_15min.csv"')

        # default life parameters

        self.life_param_dict = LIFE_PARAMETERS

        if "transformer_life_parameters.csv" not in os.listdir(self.config_dict["extra_data_path"]):
            self.logger.info("'transformer_life_parameters.csv' does not exist using default \
                            transformer life parameters")
        else:
            life_parameters = pd.read_csv(os.path.join(self.config_dict["extra_data_path"], \
                                        "transformer_life_parameters.csv"))
            if set(['Parameters','Value']).issubset(set(life_parameters.columns)):
                life_param_dict = dict(zip(life_parameters['Parameters'],life_parameters['Value']))
                self.life_param_dict = {**self.life_param_dict, **life_param_dict}
            
            else:
                self.logger.warning("'Parameters' and 'Value' column does not exist \
                                         in 'transformer_life_parameters.csv' using default values")


        self.logger.info('TransformerMetric class initiallized')

    def get_losses(self):
        """ retruns total losses from all transformers , updates each timestamp"""
        return self.losses

    def compute_lossoflife(self,trans_loading: float,temperature: (int,float),life_param_dict: dict) -> (int,float):

        # Initial stff
        TransformerLoadingList,  TemperatureData = [trans_loading,trans_loading],  [temperature,temperature]
        theta_ii = life_param_dict['theta_i']
        
        # Outer iteration loop to make sure convergence
        for _ in range(int(life_param_dict['num_of_iteration'])):
            # Storing Hot spot temperature of Transformer
            TransformerHotSpotTemperatureList = []

            # Loop through all loading values
            for k in range(len(TransformerLoadingList)):
                theta_u = life_param_dict['theta_fl'] * pow((TransformerLoadingList[k] 
                            * TransformerLoadingList[k] * life_param_dict['R'] + 1) \
                            / (life_param_dict['R'] + 1), life_param_dict['n'])

                theta_not = (theta_u - theta_ii) * (1 - math.exp(-0.25 \
                                / life_param_dict['tau'])) + theta_ii
                theta_ii = theta_not
                theta_g = life_param_dict['theta_gfl'] * pow(TransformerLoadingList[k],2 \
                            * life_param_dict['m'])
                theta_hst = theta_not + TemperatureData[k] + theta_g
                TransformerHotSpotTemperatureList.append(theta_hst)
            theta_ii = theta_hst - TemperatureData[k] - theta_g

        # Compute Loss of Life of transformer using Hot Spot temperature array
        loss_of_life = sum([100 * self.config_dict["simulation_time_step (minute)"] / (60*pow(10,life_param_dict['A'] + 
                    life_param_dict['B'] / (el + 273))) for el in [TransformerHotSpotTemperatureList[0]]])

        return loss_of_life

    def get_totallossoflife(self):

        """ returns a sum of loss of life from all transformers 
        : updates in each time step.
        """
        return self.totallol

    
    def update(self,dss_instance,current_time,timeseries_record,count):

        """ update function must be present """

        super().update(dss_instance,current_time,timeseries_record)
        
        # loop through all transformers

        if self.config_dict['export_transloadings']:
            if self.export_start_time <= current_time <= self.export_end_time:
                self.transloading['TimeStamps'].append(current_time)
        
        self.dss_instance.Circuit.SetActiveClass('Transformer')
        flag = self.dss_instance.Transformers.First()

        while flag>0:
           
            transformer_name = self.dss_instance.Transformers.Name()
            transformercomplexcurrent = self.dss_instance.CktElement.Currents()
            transformer_primarycurrent = transformercomplexcurrent[:int(0.5*len(transformercomplexcurrent))]
            transformer_current_limit = self.dss_instance.CktElement.NormalAmps()
            transformercurrent = [math.sqrt(i ** 2 + j ** 2) for i, j in zip(transformer_primarycurrent[::2], \
                            transformer_primarycurrent[1::2])]
            loading = max(transformercurrent)/transformer_current_limit
            

            # Efficiency block
            self.active_losses[transformer_name] += self.dss_instance.CktElement.Losses()[0]

            # update total losses
            self.losses += self.dss_instance.CktElement.Losses()[0]

            complex_power = self.dss_instance.CktElement.Powers()
            frombuspower, tobuspower = sum(complex_power[:int(.5*len(complex_power)):2]), \
                                        sum(complex_power[int(.5*len(complex_power))::2])
            self.active_power[transformer_name] += max(abs(frombuspower),abs(tobuspower))
            efficiency = 100 - self.active_losses[transformer_name] \
                                /(10*self.active_power[transformer_name]) if \
                            self.active_power[transformer_name]>0.01 else 100
            self.metric['TE'][transformer_name] = efficiency

            # overgeneration block
            overgeneration = max(tobuspower - frombuspower,0)
            self.metric['TOG'][transformer_name] += overgeneration*self.config_dict['simulation_time_step (minute)']/60
            
            # Transformer loading risk index block
            gamma = loading - 1 if loading>1 else 0
            #self.gamma[transformer_name] = gamma
            self.metric['TLRI'][transformer_name] += (len(self.transformer_cust_down[transformer_name]) \
                                            /self.dss_instance.Loads.Count())*gamma \
                                        *self.config_dict["simulation_time_step (minute)"]*100/count
            
            # update impacted customers list if violation exists
            if gamma > 0:
                self.customers_impacted = list(set(self.customers_impacted) \
                            .union(set(self.transformer_cust_down[transformer_name])))

            # update gamma for customers: depth of violation
            for load_name in self.transformer_cust_down[transformer_name]:
                if self.gamma[load_name] < gamma:
                    self.gamma[load_name] = gamma

            # Transformer loss of life
            loss_of_life = self.compute_lossoflife(loading,self.temperature_data['Temperature'][current_time],
                                self.life_param_dict) if loading < MAX_TRANS_LOADING else 0

            self.metric['TLOL'][transformer_name] +=  loss_of_life
            self.totallol += loss_of_life

            # Export transformer loadings
            if self.config_dict['export_transloadings']:
                if self.export_start_time <= current_time <= self.export_end_time:
                    self.transloading[transformer_name].append(loading)

            if timeseries_record:
                
                # update time series efficiency
                loss_daily = self.active_losses[transformer_name] - self.pre_act_losses[transformer_name]
                power_daily = self.active_power[transformer_name] - self.pre_act_power[transformer_name]
                efficiency_daily = 100 - loss_daily/(10*power_daily) if power_daily>0.01 else 100
                self.timeseries_metric['TE'][transformer_name].append(efficiency_daily)
                self.pre_act_losses[transformer_name] = self.active_losses[transformer_name]
                self.pre_act_power[transformer_name] = self.active_power[transformer_name]

                # update timeseries overgeneration
                previousgeneration = self.metric['TOG'][transformer_name] \
                                - sum(self.timeseries_metric['TOG'][transformer_name])
                self.timeseries_metric['TOG'][transformer_name].append(previousgeneration)

                # update timeseries transformer loading risk index
                previousvalue = self.metric['TLRI'][transformer_name] \
                                - sum(self.timeseries_metric['TLRI'][transformer_name])
                self.timeseries_metric['TLRI'][transformer_name].append(previousvalue)

                # update timeseries transformer loading risk index
                previouslossoflife = self.metric['TLOL'][transformer_name] \
                                - sum(self.timeseries_metric['TLOL'][transformer_name])
                self.timeseries_metric['TLOL'][transformer_name].append(previouslossoflife)
            
            flag = self.dss_instance.Transformers.Next()
