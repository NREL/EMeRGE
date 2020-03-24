class TomlDictForDashboard:

    def __init__(self):

        self.toml_dict = {
            "Project Path" : "C:\\Users\\KDUWADI\\Desktop\\VisualizingInDashboard\\Projects",
            "Active Project" : "GWC",
            'Time Step (min)' : 15,
            'ClassicalPVTotalSimulationMinute' : 525600,
            'AdvancedPVTotalSimulationMinute' : 44640,
            'ClassicalPVMWh' : 7008,
            'AdvancedPVMWh' : 595.2,
          }

      
      
    def ReturnDict(self):
      return self.toml_dict
