"""
Author: Kapil Duwadi
Version: 0.0.1
"""


from ResultDashboard.Dashboard.CIFFDashboard import CreateApp
import dash
from ResultDashboard.ReadersContainer import *
from ResultDashboard.pyProcessData import ProcessData
from ResultDashboard.ProcessForInitialAssessment import ProcessLoadProfile
from ResultDashboard.template import TomlDictForDashboard
import os
import toml

class DashApp:

    """ A class for developing interactive dashboard. 
    
    :param SettingsTomlFilePath: A path to .toml file containg all the settings necessary for visualization
    :type SettingsTomlFilePath: str
    :return: html file
    """

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

        """ A function to launch dashboard.Takes no parameters.

        :return: http: address to visualize results
        """

        # launch App
        return self.app.run_server(debug=True, port=8060)
    
class Template:

    """ A class which generates template for visualization process including .toml file
    
    :param FolderPath: A folder path where you want to create project
    :type FolderPath: str
    :param FeederName: A name of feeder for which you want to create a project
    :type FeederName: str
    """

    def __init__(self, FolderPath, FeederName):
        
        # Create Folders
        FolderName = "DashboardTemplate"
        os.mkdir(os.path.join(FolderPath,FolderName))
        os.mkdir(os.path.join(FolderPath,FolderName,"Projects"))
        print("{} created successfully".format(os.path.join(FolderPath,FolderName,"Projects")))

        os.mkdir(os.path.join(FolderPath,FolderName,"Projects",FeederName))
        print("{} created successfully".format(os.path.join(FolderPath,FolderName,"Projects",FeederName)))

        Feederpath = os.path.join(FolderPath,FolderName,"Projects",FeederName)
        FolderCategory = ['CoordinateCSVFiles','CSVDataFiles','CSVDataFilesForAdvancedPV','InitialAssessment','PVConnection']
        for folder in FolderCategory:
            os.mkdir(os.path.join(Feederpath,folder))
            print("{} created successfully".format(os.path.join(Feederpath,folder)))
        
        os.mkdir(os.path.join(Feederpath,'PVConnection','Base'))
        print("{} created successfully".format(os.path.join(Feederpath,'PVConnection','Base')))

        os.mkdir(os.path.join(Feederpath,'PVConnection','ExtraData'))
        print("{} created successfully".format(os.path.join(Feederpath,'PVConnection','ExtraData')))

        TomlFileContent = TomlDictForDashboard().ReturnDict()
        TomlFileContent["Project Path"] = os.path.join(FolderPath,"Projects")
        TomlFileContent["Active Project"] = FeederName

        TomlStrings = toml.dumps(TomlFileContent)
        TextFile = open(os.path.join(Feederpath,'settings.toml'),"w")
        TextFile.write(TomlStrings)
        TextFile.close()
        print("{} file created successfully".format(os.path.join(Feederpath,'settings.toml')))
