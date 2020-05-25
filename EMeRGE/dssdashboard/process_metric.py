# Standard libraries
import os
from datetime import datetime

# External libraries
from pyproj import Proj, transform
import pandas as pd

# Internal libraries

class CoordinateData:

    def __init__(self,settings,logger):

        self.settings = settings
        self.logger = logger

        self.coordinate_datapath  = os.path.join(self.settings['project_path'], \
                                self.settings['active_project'], 'Coordinates')
        
        self.process_line_coordinates()
        self.proces_point_coordintaes()

    def proces_point_coordintaes(self):

        # Convert coordinates into
        self.trans_xy_dict = self.convert_coordinates(pd.read_csv(os.path.join \
                            (self.coordinate_datapath,'transformer_coords.csv')))
        self.node_xy_dict = self.convert_coordinates(pd.read_csv(os.path.join \
                            (self.coordinate_datapath,'node_coords.csv')))
        self.cust_xy_dict = self.convert_coordinates(pd.read_csv(os.path.join \
                            (self.coordinate_datapath,'customer_coords.csv')))

        self.logger.info('Asset level metrics processed !!!')

    def convert_coordinates(self, dataframe):
        
        data_dict = {}
        for index in range(len(dataframe)):
            data = dataframe.loc[index]
            x,y = self.lat_long_converter(data['x'],data['y'])
            data_dict[data['component_name']] = {'x': x,'y': y}
        return data_dict

    def lat_long_converter(self,x1, y1):
        
        inProj = Proj(init='epsg:32644')
        outProj = Proj(init='epsg:4326')
        x2, y2 = transform(inProj, outProj, x1, y1)
        return y2, x2

    def process_line_coordinates(self):
        
        line_coordinates_data = pd.read_csv(os.path.join(self.coordinate_datapath, \
                                    'line_coords.csv'))
        
        self.x_lines, self.y_lines = [],[]
        self.initial_x, self.initial_y = [],[]
        self.line_coordinate_dict = {}

        for index in range(len(line_coordinates_data)):
            
            line_data = line_coordinates_data.loc[index]
            
            start_x, start_y = self.lat_long_converter(line_data['x1'],line_data['y1'])
            end_x, end_y = self.lat_long_converter(line_data['x2'],line_data['y2'])

            self.initial_x.extend([start_x,end_x])
            self.initial_y.extend([start_y, end_y])

            self.x_lines.extend([start_x,end_x,None])
            self.y_lines.extend([start_y,end_y,None])

            line_name = line_data['component_name']

            self.line_coordinate_dict[line_name] = {
                'x':(start_x+end_x)/2,
                'y':(start_y+end_y)/2
            }

        self.initial_x, self.initial_y = (max(self.initial_x)+min(self.initial_x))/2, \
                                            (max(self.initial_y)+min(self.initial_y))/2
        
        self.logger.info('Line coordinates processed !!!')

    
class MetricData:

    def __init__(self,settings,foldername,logger):

        self.settings = settings
        self.logger = logger

        self.asset_metrics = ['NVRI','LLRI','TLRI','CRI','TE','LE','TLOL','TOG']
        self.system_metrics = ['SARDI_voltage','SARDI_line', 'SARDI_transformer',\
                    'SARDI_aggregated','SE_line','SE_transformer','SE','SATLOL','SOG']
        
        self.metric_datapath = os.path.join(self.settings['project_path'], \
                            self.settings['active_project'], foldername)


        self.process_system_metrics()
        self.process_timeseries_system_metrics()
        self.process_asset_level_metric()

        self.logger.info('MetricData object initiallized !!!')

    def process_asset_level_metric(self):

        # Process for Asset Level Metrics and PV coordinates(this is yet not used in dashboard)
        self.asset_ts, self.asset = {}, {}

        for folder in os.listdir(self.metric_datapath):
            
            self.asset_ts[folder],self.asset[folder] = {},{}
            
            for metric in self.asset_metrics:
                self.asset[folder][metric] = pd.read_csv(os.path.join(self.metric_datapath, \
                                    folder,metric+'.csv'))

                self.asset_ts[folder][metric] = pd.read_csv(os.path.join(self.metric_datapath, \
                                folder,metric+'_timeseries.csv'),parse_dates=['TimeStamps'])

    def process_timeseries_system_metrics(self):

        self.system_timeseries_dict = {}
        self.extended_list_ts = ['TimeStamps'] + self.system_metrics

        for folder in os.listdir(self.metric_datapath):

            self.system_timeseries_dict[folder] = {metric:[] for metric in self.extended_list_ts}

            metric_data = pd.read_csv(os.path.join(self.metric_datapath,
                                    folder, 'System_timeseries.csv'),parse_dates=['TimeStamps'])

            for keys in self.system_timeseries_dict[folder].keys():
                self.system_timeseries_dict[folder][keys] = list(metric_data[keys])
        
        self.logger.info('System level time metrics processed !!!')

    def process_system_metrics(self):

        self.extended_list = ['Scenarios','x_val'] + self.system_metrics
        self.system_metrics_dict = {metric:[] for metric in self.extended_list}
        
        self.pv_scenarios = [folder for folder in os.listdir(self.metric_datapath)]
        for folder in os.listdir(self.metric_datapath):

            scenario = folder.split('-')[0] + '-' + folder.split('-')[2] if folder !='Base' else folder
            self.system_metrics_dict['Scenarios'].append(scenario)

            x = 0 if folder=='Base' else float(folder.split('%')[0])
            self.system_metrics_dict['x_val'].append(x)

            # Read systemlevelmetrics.csv
            metric_data = pd.read_csv(os.path.join(self.metric_datapath, \
                                folder,'System.csv'))

            metric_data_dict = dict(zip(list(metric_data['component_name']),
                                    list(metric_data['values'])))

            for metric,value in metric_data_dict.items():
                self.system_metrics_dict[metric].append(value)

        # Now let's sort all the values
        for keys, values in self.system_metrics_dict.items():
            if keys!='x_val':
                sortedx,sortedvalue = zip(*sorted(zip(self.system_metrics_dict['x_val'],values)))
                self.system_metrics_dict[keys] = sortedvalue
        self.system_metrics_dict['x_val'] = sortedx
        
        # Making easier to generate plots

        violation_metrics = ['Scenarios', 'x_val','SARDI_voltage','SARDI_line',
                                'SARDI_transformer','SARDI_aggregated']
        efficiency_metrics = ['Scenarios', 'x_val','SE_line','SE_transformer','SE']
        loss_of_life_metrics  =['Scenarios', 'x_val','SATLOL']
        overgeneration_metrics =['Scenarios', 'x_val','SOG']

        self.violation_dict, self.eff_dict, self.lol_dict, self.og_dict = {},{},{},{}

        for metric in violation_metrics:
            self.violation_dict[metric] = self.system_metrics_dict[metric]

        for metric in efficiency_metrics:
            self.eff_dict[metric] = self.system_metrics_dict[metric]

        for metric in loss_of_life_metrics:
            self.lol_dict[metric] = self.system_metrics_dict[metric]

        for metric in overgeneration_metrics:
            self.og_dict[metric] = self.system_metrics_dict[metric]

        self.logger.info('System level metrics processed !!!')