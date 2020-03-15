
from DSSRiskAnalyzer.SubModulesContainer.ReadersContainer import *
from DSSRiskAnalyzer.pyRunTimeSeriesPowerFlow import OpenDSS
from DSSRiskAnalyzer.template import TomlDict
import os

class RunRiskAnalysis:

    def __init__(self, SettingsTomlFilePath):

        SimulationSettings = ReadFromFile(SettingsTomlFilePath)

        print('<-------------Running Risk Analaysis on "{}" feeder------------>'.format(
            SimulationSettings['Active_Feeder']))

        # Read necessary files present in 'ExtraData' Folder - must be defined in 'settings.toml' file

        ExtraDataFilesDirectory = os.path.join(SimulationSettings['Project path'], SimulationSettings['Active_Feeder'],
                                               'ExtraData')

        ExtraDataFilesDataStoredByIndicator = {}
        for fileindicator, filename in SimulationSettings["FileNames"].items():
            ExtraDataFilesDataStoredByIndicator[fileindicator] = ReadFromFile(
                os.path.join(ExtraDataFilesDirectory, filename))

        # Running simulation for all scenarios present within 'DSSScenarios' folder

        DSSFilePathDirectory = os.path.join(SimulationSettings['Project path'], SimulationSettings['Active_Feeder'],
                                            'DSSScenarios')

        # Creating folders if not already present

        ExportFolderPath = os.path.join(SimulationSettings['Project path'], SimulationSettings['Active_Feeder'],
                                        'Exports')
        if not os.path.exists(ExportFolderPath): os.mkdir(ExportFolderPath)
        CategoryFolderPath = os.path.join(ExportFolderPath, SimulationSettings['Active_Scenario'])
        if not os.path.exists(CategoryFolderPath): os.mkdir(CategoryFolderPath)

        for DSSScenario in os.listdir(DSSFilePathDirectory):
            print('Running Simulation for {} scenario'.format(DSSScenario))

            ExportPath = os.path.join(CategoryFolderPath, DSSScenario)

            DSSpath = os.path.join(DSSFilePathDirectory, DSSScenario, SimulationSettings['DSSfilename'])

            a = OpenDSS(DSSpath, SimulationSettings, ExtraDataFilesDataStoredByIndicator, ExportPath)
            del a

        print("Analysis complete !!!")

class Template:

    def __init__(self, FolderPath, FeederName):
        
        # Create Folders
        FolderName = "DSSRiskAnalyzerTemplate"
        os.mkdir(os.path.join(FolderPath,FolderName))
        os.mkdir(os.path.join(FolderPath,FolderName,"Projects"))
        print("{} created successfully".format(os.path.join(FolderPath,FolderName,"Projects")))

        os.mkdir(os.path.join(FolderPath,FolderName,"Projects",FeederName))
        print("{} created successfully".format(os.path.join(FolderPath,FolderName,"Projects",FeederName)))

        Feederpath = os.path.join(FolderPath,FolderName,"Projects",FeederName)
        FolderCategory = ['AnalysisScenarios','DSSScenarios','ExtraData']
        for folder in FolderCategory:
            os.mkdir(os.path.join(Feederpath,folder))
            print("{} created successfully".format(os.path.join(Feederpath,folder)))
        
        os.mkdir(os.path.join(Feederpath,'AnalysisScenarios','Category'))
        print("{} created successfully".format(os.path.join(Feederpath,'AnalysisScenarios','Category')))

        TomlFileContent = TomlDict()
        TomlFileContent["Project path"] = os.path.join(FolderPath,"Projects")
        TomlFileContent["Active_Feeder"] = FeederName
        TomlFileContent["Active_Scenario"] = 'Category'

        TomlStrings = toml.dumps(TomlFileContent)
        TextFile = open(os.path.join(Feederpath,'AnalysisScenarios','Category','settings.toml'),"w")
        TextFile.write(TomlStrings)
        TextFile.close()
        print("{} file created successfully".format(os.path.join(Feederpath,'AnalysisScenarios','Category','settings.toml')))

if __name__ == "__main__":

    # Read all the settings to perform simulation

    #SimulationSettingsTomlFilePath = r'C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\Distribution_Metric_Computing_Tool\Projects\GR_PALAYAM\AnalysisScenarios\Category_March\settings.toml'
    CategoryPath = r"C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\Distribution_Metric_Computing_Tool\Projects\GWC\AnalysisScenarios"
    for category in os.listdir(CategoryPath):
        SimulationSettingsTomlFilePath = os.path.join(CategoryPath,category,'settings.toml')
        RunRiskAnalysis(SimulationSettingsTomlFilePath)

