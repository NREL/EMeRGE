# Standard libraries
import os
import json
import logging

# External libraries
import dash

# Internal libraries
from dssdashboard.constants import FOLDER_LIST, LOG_FORMAT, DEFAULT_CONFIGURATION, VALID_SETTINGS
from dssdashboard.validate import folder_validate
from dssdashboard.dashboard_create import CreateApp
from dssdashboard.process_load_profile import LoadProfileData
from dssdashboard.process_metric import MetricData, CoordinateData
from dssglobal.validate import validate

class AppServer:

    def __init__(self,config_json=None):

        
        if config_json != None:
        
            self.logger = logging.getLogger()

            if isinstance(config_json,dict):
                self.config = config_json
            elif isinstance(config_json,str):
                if config_json.endswith('.json'):
                    with open(config_json,"r") as json_file:
                        self.config = json.load(json_file)

            self.config = {**DEFAULT_CONFIGURATION,**self.config}

            # Validate type
            validate(self.config,VALID_SETTINGS)

            self.active_project = os.path.join(self.config['project_path'],self.config['active_project'])
            
            message = folder_validate(self.active_project)

            if self.config['log_filename'].endswith('.log'):
                logging.basicConfig(format=LOG_FORMAT,level='DEBUG', \
                                filename=os.path.join(self.active_project,self.config['log_filename']))
            else:
                logging.basicConfig(format=LOG_FORMAT,level='DEBUG')


            if message == 'sucess on validation !':
                self.logger.info(message)
            else:
                self.logger.warning(message)

            self.initiallize_app()

    def initiallize_app(self):

        
        if 'Profile' in os.listdir(self.active_project):
            self.profile_object = LoadProfileData(self.config,self.logger)
        else:
            self.profile_object = None

        if 'PVMetrics' in os.listdir(self.active_project):
            self.pv_object = MetricData(self.config,'PVMetrics',self.logger)
        else:
            self.pv_object = None

        if 'AdvancedPVMetrics' in os.listdir(self.active_project):
            self.advanced_pv_object = MetricData(self.config,'AdvancedPVMetrics',self.logger)
        else:
            self.advanced_pv_object = None

        if 'Coordinates' in os.listdir(self.active_project):
            self.coord_object = CoordinateData(self.config,self.logger)
        else:
            self.coord_object = None

         # Sets up a app for dashboard
        self.app = dash.Dash(__name__,
                            meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],)

        # Suppress any call backs
        self.app.config["suppress_callback_exceptions"] = True

        self.logger.info('Initiallzed the app')

        # Call App Object
        self.app_object = CreateApp(self.app,self.config,self.logger, 
                    self.profile_object, self.pv_object,self.advanced_pv_object, self.coord_object)

        # Setup layout for App
        self.app.layout = self.app_object.layout()

        # Callback functions for app
        self.app_object.call_backs()

    def launch(self,port=8060):

        # launch the app 
        self.logger.info('Launching dashboard .........')
        return self.app.run_server(debug=True, port=port)


    def create_skeleton(self,project_path,active_project):

        if not os.path.exists(project_path):
            os.mkdir(r'./Project')
            project_path = r'./Project'
        
        if active_project=='': active_project='test'
        os.mkdir(os.path.join(project_path,active_project))

        for folder in FOLDER_LIST:
            os.mkdir(os.path.join(project_path,active_project,folder))
            if folder == 'PVConnection':
                os.mkdir(os.path.join(project_path,active_project,folder,'Base'))
                os.mkdir(os.path.join(project_path,active_project,folder,'ExtraData'))
        
        with open(os.path.join(project_path,active_project,'config.json'),'w') as json_file:
            json.dump(DEFAULT_CONFIGURATION,json_file)
            
if __name__ == "__main__":

    a = AppServer(r'emerge/dssdashboard/config.json')
    a.launch()