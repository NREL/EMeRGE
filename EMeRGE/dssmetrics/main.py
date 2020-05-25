# standard libraries
import json
import os
import logging
import concurrent.futures 
import copy
# internal libraries
from dssmetrics.opendss import OpenDSS 
from dssmetrics.constants import DEFAULT_ADVANCED_CONFIGURATION, VALID_SETTINGS, DEFAULT_CONFIGURATION
from dssglobal.logger import getLogger
from dssglobal.validate import validate


class MultipleOpenDSS:

    """ Higher level on top of OpenDSS class to 
    run mutiple scenarios.
    """

    def __init__(self):

        """ Constructor"""
        
        self.config_data = DEFAULT_ADVANCED_CONFIGURATION

    def create_skeleton(self,projectpath='.',feedername='Test'):

        """ Creates a skeleton for project structure """

        if not os.path.exists(projectpath):
            raise Exception(f'{projectpath} does not exist !')

        if feedername not in os.listdir(projectpath):
            os.mkdir(os.path.join(projectpath,feedername))
        
        Folder_tocreate = ['DSSScenarios','Exports','Logs','ExtraData']
        for folder in Folder_tocreate:
            if folder not in os.listdir(os.path.join(projectpath,feedername)):
                os.mkdir(os.path.join(projectpath,feedername,folder))

        json_file = open(os.path.join(projectpath,feedername,'config.json'),'w')
        json_file.write(json.dumps(DEFAULT_ADVANCED_CONFIGURATION))
        json_file.close()
        
    def simulate(self,config_data=r'dssmetrics\advanced_config.json'):
        # Read config data

        if isinstance(config_data,str):
            with open(config_data,"r") as json_file:
                configuration_data = json.load(json_file)
            self.config_data = {**self.config_data,**configuration_data}
        elif isinstance(config_data,dict):
            self.config_data = {**self.config_data,**config_data}

        # General validation
        validate(self.config_data,VALID_SETTINGS)

        # Make sure we have important stuffs
        if not os.path.exists(self.config_data["project_path"]):
            raise Exception(f"{self.config_data['project_path']} does not exist, simulation can not continue.")

        if not os.path.exists(os.path.join(self.config_data["project_path"],
                                self.config_data["active_project"])): 
            raise Exception(f"{self.config_data['active_project']} project does not exist, \
                        simulation can not continue.")
        
        self.feeder_folder = os.path.join(self.config_data["project_path"],
                                self.config_data["active_project"]) 

        if not set(['DSSScenarios','ExtraData']).issubset(set(os.listdir(self.feeder_folder))):
            raise Exception('Make sure you have both folders named correctly \
                "DSSScenarios" or "ExtraData" folder is not present.')
        
        if 'Exports' not in os.listdir(self.feeder_folder):
            os.mkdir(os.path.join(self.feeder_folder,'Exports'))
        
        self.exportfolderpath = os.path.join(self.feeder_folder,'Exports')

        if 'Logs' not in os.listdir(self.feeder_folder):
            os.mkdir(os.path.join(self.feeder_folder,'Logs'))
        
        self.logfolderpath = os.path.join(self.feeder_folder,'Logs')

        self.logger = getLogger({**self.config_data['log_settings'],**{'log_folder':self.logfolderpath}})

        self.generate_jsonlist()

        if self.config_data['parallel_simulation']:
            self.run_in_parallel()
        else:
            self.run()
    

    def generate_jsonlist(self):

        self.dsspath = os.path.join(self.config_data['project_path'], self.config_data['active_project']\
                            ,'DSSScenarios')

        self.logger.info('Running risk analysis ..')
        self.json_dict_list = []

        if self.config_data['active_scenario'] not in os.listdir(self.exportfolderpath):
            os.mkdir(os.path.join(self.exportfolderpath,self.config_data['active_scenario']))
        
        self.exportcategorypath = os.path.join(self.exportfolderpath,self.config_data['active_scenario'])

        for scenario in os.listdir(self.dsspath):

            temp_dict = {**DEFAULT_CONFIGURATION,**self.config_data}
            
            temp_dict['dss_filepath'] = os.path.join(self.dsspath,scenario)
            temp_dict['extra_data_path'] = os.path.join(self.feeder_folder,'ExtraData')

            if scenario not in os.listdir(self.exportcategorypath):
                os.mkdir(os.path.join(self.exportcategorypath ,scenario))
            
            temp_dict['export_folder'] = os.path.join(self.exportcategorypath,scenario)
            temp_dict['log_settings']['log_folder'] = self.logfolderpath
            self.json_dict_list.append(copy.deepcopy(temp_dict))
    
    def run_in_parallel(self):

        num_of_process = self.config_data['parallel_process']
        if len(self.json_dict_list) <= num_of_process:

            with concurrent.futures.ProcessPoolExecutor() as executor:
                [executor.submit(self.run_powerflow, json_dict) for json_dict \
                            in self.json_dict_list]
        else:
            with concurrent.futures.ProcessPoolExecutor() as executor:
                [executor.submit(self.run_powerflow, json_dict) for json_dict \
                            in self.json_dict_list[:num_of_process]]
            self.json_dict_list = self.json_dict_list[num_of_process:]
            self.run_in_parallel()
    
    def run_powerflow(self,json_dict):
        
        self.logger.info(f"Running simulation with settings {json_dict}................")
        instance = OpenDSS(json_dict)
        instance.qsts_powerflow()
        del instance
    
    def run(self):

        for json_dict in self.json_dict_list:
            self.run_powerflow(json_dict)            

if __name__ == '__main__':

    a = MultipleOpenDSS()
    a.simulate()
    del a
        

