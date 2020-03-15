"""
Author: Kapil Duwadi
Version: 0.0.1
"""


from ResultDashboard.Dashboard.CIFFDashboard import CreateApp
import dash
from ResultDashboard.ReadersContainer import *
from ResultDashboard.pyProcessData import ProcessData
from ResultDashboard.ProcessForInitialAssessment import ProcessLoadProfile

class DashApp:

    def __init__(self,SettingsTomlFilePath):

        # Read settings file
        #SettingsTomlFilePath = r"C:\Users\KDUWADI\Desktop\VisualizingInDashboard\Projects\settings.toml"
        
        self.DashboardSettings = ReadFromFile(SettingsTomlFilePath)
        
        self.DataObject = ProcessData(self.DashboardSettings, 'Classical')

        self.DataObjectAdvancedPV = ProcessData(self.DashboardSettings, 'Advanced', DataFolderName = 'CSVDataFilesForAdvancedPV')

        self.DataObjectInitialAssessment = ProcessLoadProfile(self.DashboardSettings)

        # Sets up a app for dashboard
        self.app = dash.Dash(__name__,meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}])

        # Suppress any call backs
        self.app.config["suppress_callback_exceptions"] = True

        # Call App Object
        self.DashApp = CreateApp(self.app,self.DashboardSettings, self.DataObject, self.DataObjectAdvancedPV, self.DataObjectInitialAssessment)

        # Setup layout for App
        self.app.layout = self.DashApp.layout()

        # Callback functions for app
        self.DashApp.Callbacks()

        return

    def Launch(self):

        # launch App
        return self.app.run_server(debug=True, port=8060)