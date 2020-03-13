
from DSSRiskAnalyzer.SubModulesContainer.ReadersContainer import *
from DSSRiskAnalyzer.pyRunTimeSeriesPowerFlow import OpenDSS
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

if __name__ == "__main__":

    # Read all the settings to perform simulation

    #SimulationSettingsTomlFilePath = r'C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\Distribution_Metric_Computing_Tool\Projects\GR_PALAYAM\AnalysisScenarios\Category_March\settings.toml'
    CategoryPath = r"C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\Distribution_Metric_Computing_Tool\Projects\GWC\AnalysisScenarios"
    for category in os.listdir(CategoryPath):
        SimulationSettingsTomlFilePath = os.path.join(CategoryPath,category,'settings.toml')
        RunRiskAnalysis(SimulationSettingsTomlFilePath)

