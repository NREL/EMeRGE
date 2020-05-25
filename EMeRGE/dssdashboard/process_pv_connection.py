# Standard libraries
import os
import shutil
import math
from datetime import datetime as dt
from datetime import timedelta
import json
import sys
# External libraries
import pandas as pd

# Internal libraries
from dssdashboard.constants import DATE_FORMAT
from dssmetrics.constants import DEFAULT_CONFIGURATION
from dssmetrics.opendss import OpenDSS

class PVConnection:

    def __init__(self, settings, logger, pv_dict, time_dict, file_dict):

        self.settings = settings
        self.logger = logger
        self.pv_dict = pv_dict
        self.time_dict = time_dict
        self.file_dict = file_dict
        self.create_new_dssfile()
        self.logger.info('PV Connection object performed simulation successfully !!!')

    def create_new_dssfile(self):

        self.working_path = os.path.join(self.settings['project_path'],
                            self.settings['active_project'],'PVConnection')

        if os.path.exists(os.path.join(self.working_path,'New')): 
            shutil.rmtree(os.path.join(self.working_path,'New'))
        os.mkdir(os.path.join(self.working_path,'New'))
        
        # Copy all the files from 'Base' folder to 'New' folder
        for file in os.listdir(os.path.join(self.working_path,'Base')):
            shutil.copy(os.path.join(self.working_path,'Base',file), \
                        os.path.join(self.working_path,'New'))

        self.add_pvsystem(os.path.join(self.working_path,'New'), \
                        'load.dss','PVsystem.dss',self.pv_dict)
        self.logger.info('PV system added successfully ..')

    def process_metrics(self):

        
        self.asset_metrics = ['NVRI', 'LLRI', 'TLRI', 'CRI', 'TE', 'LE', 'TLOL', 'TOG']
        self.system_metrics = ['SARDI_voltage', 'SARDI_line', 'SARDI_transformer', 'SARDI_aggregated', 'SE_line',
                              'SE_transformer', 'SE', 'SATLOL', 'SOG']

        
        self.metric_diff = {'NVRI':0,'CRI':0}

        for metric in self.metric_diff.keys():
            base_result = pd.read_csv(os.path.join(self.working_path,'BaseResults', metric +'.csv'))
            base_result_dict = dict(zip(list(base_result['component_name']), list(base_result['values'])))
            new_result = pd.read_csv(os.path.join(self.working_path,'NewResults', metric +'.csv'))
            new_result_dict = dict(zip(list(new_result['component_name']), list(new_result['values'])))
            
            if metric == 'NVRI':
                self.metric_diff[metric] = new_result_dict[self.busname] \
                                - base_result_dict[self.busname]
            if metric == 'CRI':
                self.metric_diff[metric] = new_result_dict[self.pv_dict['LoadName']] \
                                - base_result_dict[self.pv_dict['LoadName']]

        return self.metric_diff

    def process_results(self):

        result_dict = {}
        for case in ['Base','New']:
            result_dict[case] = {}
            result_path = os.path.join(self.working_path,case+'Results')
            for param in ['voltages','lineloading','transloading']:
                result_dict[case][param] = pd.read_csv(os.path.join(result_path,param+'.csv'))


        result_diff_dict = {}

        for param in ['voltages','lineloading','transloading']:
            result_diff_dict[param] = {'max_diff':{},'Base':{}}
            for cols in list(result_dict['Base'][param].columns):
                if cols != 'TimeStamps':
                    difference= [x[1]-x[0] for x in zip(list(result_dict['Base'][param][cols]),\
                                        list(result_dict['New'][param][cols]))]

                    result_diff_dict[param]['max_diff'][cols] = max(difference)
                    result_diff_dict[param]['Base'][cols] = \
                        result_dict['Base'][param][cols].tolist()[difference.index(max(difference))]
        
        return result_diff_dict
    
    def run_powerflow(self):

        self.startdate = dt.strptime(self.time_dict['Time'],DATE_FORMAT)

        if self.time_dict['Mode'] == 'Snapshot':
            self.enddate = self.startdate+timedelta(minutes=self.settings['time_step(min)'])
            self.record_every  = 1


        if self.time_dict['Mode'] == 'Daily':
            self.enddate = self.startdate+timedelta(hours=24)
            self.record_every = 1


        month  = self.startdate.month + 1 if self.startdate.month <12 else 1
        if self.time_dict['Mode'] == 'Monthly':
            self.enddate = dt(self.startdate.year, month, self.startdate.day, self.startdate.hour, \
                             self.startdate.minute, self.startdate.second)
            self.record_every = int(1440/self.settings['time_step(min)'])
        
        # Create a Exports  and Logs folder
        folder_list = ['BaseResults','NewResults','Logs']
        for folder in folder_list:
            if folder not in os.listdir(self.working_path):
                os.mkdir(os.path.join(self.working_path,folder))

        config_dict = {**DEFAULT_CONFIGURATION,**self.settings['pv_connection']}
        
        config_dict['dss_filepath'] = os.path.join(self.working_path,'New')
        config_dict['extra_data_path'] = os.path.join(self.working_path,'ExtraData')
        config_dict['export_folder'] = os.path.join(self.working_path,'NewResults')
        config_dict['start_time'] = dt.strftime(self.startdate,"%Y-%m-%d %H:%M:%S")
        config_dict['end_time'] = dt.strftime(self.enddate,"%Y-%m-%d %H:%M:%S")
        config_dict['record_every'] = self.record_every
        config_dict["export_voltages"] =  True
        config_dict["export_lineloadings"] = True
        config_dict["export_transloadings"] = True
        config_dict["export_start_date"] = dt.strftime(self.startdate,"%Y-%m-%d %H:%M:%S")
        config_dict["export_end_date"] =  dt.strftime(self.enddate,"%Y-%m-%d %H:%M:%S")
        config_dict["log_settings"]['log_folder'] =  os.path.join(self.working_path,'Logs')
        config_dict["log_settings"]['log_filename'] =  os.path.join(self.working_path,'new.log')
        

        with open(os.path.join(self.working_path, 'new_config.json'), "w") as json_file:
            json.dump(config_dict,json_file)

        # Modify config for Base
        config_dict['dss_filepath'] = os.path.join(self.working_path,'Base')
        config_dict['export_folder'] = os.path.join(self.working_path,'BaseResults')
        config_dict["log_settings"]['log_filename'] =  os.path.join(self.working_path,'base.log')

        with open(os.path.join(self.working_path, 'base_config.json'), "w") as json_file:
            json.dump(config_dict,json_file)
        
        self.logger.info('configuration file created for PV connection study ..')

        # metric analysis for both new and base case
        a = OpenDSS(os.path.join(self.working_path,'new_config.json'))
        a.qsts_powerflow()
        del a
        a = OpenDSS(os.path.join(self.working_path,'base_config.json'))
        a.qsts_powerflow()
        del a

    def add_pvsystem(self,root_path, load_dssfile, pvdssfile, pv_dict):

        phases = 1 if pv_dict['Phases'] != 'RYB' else 3
        phase2num = {"R":1,"Y":2,"B":3}
        
        line_to_add = ['new',
                     'pvsystem.{}'.format(pv_dict['LoadName']),
                     'irradiance={}'.format(pv_dict['Irradiance']),
                     'kva={}'.format(float(pv_dict['Capacity']*pv_dict['InverterOverSizeFactor'])),
                     'pmpp={}'.format(float(pv_dict['Capacity'])),
                     'kvar={}'.format(pv_dict['KVAR']),
                     '%cutin={}'.format(pv_dict['CutIn']),
                     '%cutout={}'.format(pv_dict['CutOut']),
                     'yearly={}'.format(pv_dict['Profile'])]

        with open(os.path.join(root_path,load_dssfile)) as fp:

            readline = fp.readline()

            while readline:

                linecontent = str(readline.strip())
                if pv_dict['LoadName'].lower() in linecontent.lower():
                    linecontentlist = linecontent.split(' ')
                    for element in linecontentlist:
                        if 'bus1=' in element:
                            bus1string = element
                        if 'kv=' in element:
                            kvstring= element
                        if 'phases=' in element:
                            phasestring = element
                    break

                readline = fp.readline()
        fp.close()

        self.busname = bus1string.split('=')[1].split('.')[0]

        if phases>=float(phasestring.split('=')[1]):
            line_to_add.append(bus1string)
            line_to_add.append(phasestring)
            line_to_add.append(kvstring)

        if phases < float(phasestring.split('=')[1]):
            line_to_add.append(bus1string.split('.')[0]+'.'+phase2num[pv_dict['Phases']]+'.0')
            line_to_add.append('phase={}'.format(phases))
            line_to_add.append('kv={}'.format(float(kvstring.split('=')[1])/math.sqrt(3)))


        line_string = ' '.join(line_to_add)

        if pvdssfile not in os.listdir(root_path):
            newfile = open(os.path.join(root_path,pvdssfile), "w")
            newfile.write(line_string)
            newfile.close()
        else:
            line_content = []
            with open(os.path.join(root_path,pvdssfile),'r') as fp:
                line = fp.readline()
                while line:

                    if self.file_dict['Delete']:
                        if not pv_dict['LoadName'] in line:
                            line_content.append(line)
                    else:
                        line_content.append(line)

                    line = fp.readline()
            
            line_content_string = ''.join(line_content)

            if pv_dict['LoadName'] not in line_content_string and self.file_dict['Delete']==False:
                line_content_string = line_content_string + '\n' + line_string

            with open(os.path.join(root_path,pvdssfile),'w') as fp:
                fp.write(line_content_string)
            
        if self.file_dict['Accept'] or self.file_dict['Delete']:
            shutil.copy(os.path.join(root_path,pvdssfile),
                os.path.join(self.working_path,'Base'))
            self.logger.info('file copied from New folder to Base folder')
