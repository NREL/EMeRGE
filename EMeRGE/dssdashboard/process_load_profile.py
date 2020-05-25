# Standard libraries
import os
from datetime import datetime as dt
from datetime import timedelta

# External libraries
import pandas as pd

class LoadProfileData:

    def __init__(self,settings, logger):

        self.logger = logger
        self.settings = settings

        # Read all csv files
        self.read_files()

        self.group_kw = self.consumer_data.groupby('cust_type').sum()['kw'].to_dict()
        self.timeseries, self.timeseriesdict = [],{}

        for group, load in self.group_kw.items():
            
            group_timeseries = [mult*load for mult in self.dataframe_dict[group]]
            self.timeseriesdict[group] = group_timeseries

            if self.timeseries  == []:
                self.timeseries = group_timeseries
            else:
                self.timeseries = [sum(x) for x in zip(self.timeseries,group_timeseries)]

        self.logger.info('Profile object instantiated !!')

    
    def get_data(self,pv_pen: float, date):

        self.timeseries_pv, self.timeseriesdict_pv = [],{}
        self.pvgeneration = []

        # find out the peak and peak_index
        self.peak = max(self.timeseries)
        self.peak_index = self.timeseries.index(self.peak)

        for group, load in self.group_kw.items():

            load_at_peak = self.dataframe_dict[group][self.peak_index]*load
            base_load = [el*load for el in self.dataframe_dict[group]]
            solar_gen = [load_at_peak*pv_pen/100*el for el in self.solar_data]
            net_load = [x[0] - x[1] for x in zip(base_load,solar_gen)]
            self.timeseriesdict_pv[group] = net_load

            if self.timeseries_pv == []:
                self.timeseries_pv = net_load
                self.pvgeneration = solar_gen
            else:
                self.timeseries_pv = [sum(x) for x in zip(self.timeseries_pv,net_load)]
                self.pvgeneration = [sum(x) for x in zip(self.pvgeneration,solar_gen)]
            
        # Let's arange in descending order to plot load duration curve
        self.sorted_timeseries_pv, self.ids = zip(*sorted(zip(self.timeseries_pv, \
                                range(len(self.timeseries_pv))),reverse=True))

        self.sorted_timeseriesdict_pv = {}
        for group, array in self.timeseriesdict_pv.items():

            temp_array = [array[index] for index in self.ids]
            self.sorted_timeseriesdict_pv[group] = temp_array

        data_len = len(self.sorted_timeseries_pv)
        self.sorted_timeseriesdict_pv['TimeStamp'] = [index*100/data_len for index in range(data_len)]
        
        # Separate load data for a day
        self.datelist = [dt(self.settings['year'],1,1,0,0,0) \
                    + timedelta(minutes=self.settings['time_step(min)'])*i \
                            for i in range(len(self.timeseries_pv))]
        
        if ":" in date:
            self.date = dt.strptime(date,'%Y-%m-%d %H:%M:%S')
        else:
            self.date = dt.strptime(date,'%Y-%m-%d')

        self.daily_data = {'TimeStamp':[el for el in self.datelist 
                    if el.day==self.date.day and el.month==self.date.month]}

        for group, array in self.timeseriesdict_pv.items():

            temp_array = []
            for date, load in zip(self.datelist,array):
                if date.day == self.date.day:
                    temp_array.append(load)
            self.daily_data[group] = temp_array

        # Sample load duration data
        self.sorted_sample_dict = {}
        
        for group, array in self.sorted_timeseriesdict_pv.items():
            chunk_size = int(len(array)/1000) if len(array)>3000 else 1
            self.sorted_sample_dict[group] = [array[index] for index in range(0,len(array),chunk_size)]
        
        # Get statistics about load profile
        absolute_load = [abs(value) for value in self.timeseries_pv]
        max_net_gen = 'NA' if pv_pen==0 else -round(min(self.timeseries_pv)/1000,2)
        load_factor = round(sum(self.timeseries_pv)/(len(self.timeseries_pv)*max(self.timeseries_pv)),2)


        col_names = ['Peak load (MW)','Minimum load (MW)', 'Maximum solar generation (MW)', \
                        'Maximmum Net Generation (MW)', 'Load factor']
        
        val_list = [round(max(self.timeseries_pv)/1000,2),
                    round(min(absolute_load)/1000,2),
                    round(max(self.pvgeneration)/1000,2),
                    max_net_gen,
                    load_factor]

        time_list = [self.timeseries_pv.index(max(self.timeseries_pv)),
                     absolute_load.index(min(absolute_load)),
                     self.pvgeneration.index(max(self.pvgeneration)),
                     self.timeseries_pv.index(min(self.timeseries_pv)),
                     'NA']
        
        if max_net_gen == 'NA': time_list[3] = 'NA'

        for id, value in enumerate(time_list):
            if value != 'NA':
                time_list[id] = self.datelist[value]

        self.df_stat = pd.DataFrame({'Parameters': col_names,'Value': val_list, 'Time': time_list})

        return self.sorted_sample_dict, self.daily_data, self.df_stat
    
    
    def read_files(self):

        # Make sure all file exists
        fileslist = ['residential.csv','commercial.csv','industrial.csv',
                    'agricultural.csv','consumer.csv','solarmult.csv']

        file_path = os.path.join(self.settings['project_path'], \
                            self.settings['active_project'],'Profile')
        
        if not set(fileslist).issubset(set(os.listdir(file_path))):
            raise Exception(f"At least one of the file in list {','.join(fileslist)} \
                    is missing in folder path {file_path}")

        
        file_dict = {'residential':'residential.csv',
                    'commercial':'commercial.csv',
                    'industrial':'industrial.csv',
                    'agricultural':'agricultural.csv'}
        self.dataframe_dict  = {}

        for consumertype, filename in file_dict.items():
            self.dataframe_dict[consumertype] = list(pd.read_csv(os.path.join(file_path,  \
                                                filename),header=None)[0])
        
        self.consumer_data =  pd.read_csv(os.path.join(file_path,'consumer.csv'))
        self.solar_data = list(pd.read_csv(os.path.join(file_path,'solarmult.csv'),header=None)[0])

        self.logger.info(f'Files read successfully from folder path {file_path}')
