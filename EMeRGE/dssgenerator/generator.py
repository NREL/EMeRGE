# Standard libraries
import os,pathlib
import json
import shutil
import logging

# External libraries

# Internal libraries
from dssgenerator.reader import Reader
from dssgenerator.writer import Writer
from dssgenerator.constants import LOG_FORMAT, DEFAULT_CONFIGURATION, VALID_SETTINGS
from dssglobal.validate import validate
from dssglobal.logger import getLogger


class CSV2DSS:
    """ A class for generating .dss files using .csv files from :class:`CSVformatter` 
    
    :param settings_toml_file: A path to .toml file containg all the settings necessary for conversion
    :type settings_toml_file: str
    :return: dss files
    """

    def __init__(self, config_file=None):
        
        if config_file != None:
        
            if isinstance(config_file,dict):
                config_dict = config_file
            else:
                with open(config_file,'r') as json_file:
                    config_dict = json.load(json_file)
            
            self.config_dict = {**DEFAULT_CONFIGURATION,**config_dict}

            validate(self.config_dict,VALID_SETTINGS)

            self.logger = getLogger(self.config_dict['log_settings'])

            self.logger.info('Settings file validated ...')

            self.create_scenario_dict()
            self.network = Reader(self.config_dict,self.logger)

            self.export_dsspath = os.path.join(self.config_dict['project_path'],'ExportedDSSfiles')

            self.clear_folder(self.export_dsspath)
            self.logger.info("Created or cleared export folder")

            for keys, values in self.scenario_dict.items():
                self.logger.info(f">>>> Creating DSS files for {keys} scenario ................")
                
                if values['PPV_capacity'] in [0,100] and values['PPV_customers'] in [0,100]:
                    Writer( self.network, 
                            self.config_dict,
                            self.logger,
                            os.path.join(self.export_dsspath,keys), 
                            values['PPV_customers']/100,
                            values['PPV_capacity']/100)
                else:
                    if self.config_dict['number_of_monte_carlo_run'] == 1:
                        Writer( self.network, 
                            self.config_dict,
                            self.logger,
                            os.path.join(self.export_dsspath,keys), 
                            values['PPV_customers']/100,
                            values['PPV_capacity']/100)

                    else:
                        if self.config_dict['number_of_monte_carlo_run'] <1:
                            raise ValueError(f'Number of monte carlo run must be greater than 1')

                        if not os.path.exists(os.path.join(self.export_dsspath,keys)): 
                            os.mkdir(os.path.join(self.export_dsspath,keys))
                        for j in range(self.config_dict['number_of_monte_carlo_run']):
                            Writer( self.network, 
                                    self.config_dict,
                                    self.logger,
                                    os.path.join(self.export_dsspath,keys,'monte_carlo_'+str(j)), 
                                    values['PPV_customers']/100,
                                    values['PPV_capacity']/100)
    
    def create_skeleton(self,project_path,feeder_name):

        if os.path.exists(project_path):
    
            folder_list = [feeder_name,'ExtraCSVs']
            for folder in folder_list:
                if folder not in os.listdir(project_path):
                    os.mkdir(os.path.join(project_path,folder))

            with open(os.path.join(project_path,'config.json'),'w') as json_file:
                json.dump(DEFAULT_CONFIGURATION,json_file)
        

    def create_scenario_dict(self):
        
        self.scenario_dict = {}
        self.scenario_dict['Base'] = {'PPV_customers': 0, 'PPV_capacity': 0}
        
        for ppv_cap in range(self.config_dict['PV_capacity_step']):
            for ppv_cust  in range(self.config_dict['PV_customers_step']): 
                customer = 100*(ppv_cust+1)/(self.config_dict['PV_customers_step'])
                capacity = 100*(ppv_cap+1)/(self.config_dict['PV_capacity_step'])
                key_name = str(customer) + '%-customer-'+str(capacity)+'%-PV'
                self.scenario_dict[key_name] = {'PPV_customers': customer , 'PPV_capacity':capacity }
    
    def clear_folder(self,path):
        
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        for root, dirs, files in os.walk(path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        return

if __name__ == '__main__':
    CSV2DSS(r'dssgenerator/config.json')
