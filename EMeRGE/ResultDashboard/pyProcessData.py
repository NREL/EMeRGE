import os
from ResultDashboard.ReadersContainer import *
from datetime import datetime
from pyproj import Proj, transform

class ProcessData:

    def __init__(self, Settings, TypePV, DataFolderName = 'CSVDataFiles' ):

        self.Settings = Settings
        self.TypePV = TypePV

        self.AssetLevelMetrics = ['NVRI','LVRI','TVRI','CRI','TE','LE','TLOF','TOG']
        self.SystemMetrics = ['SARDI_voltage','SARDI_line', 'SARDI_transformer','SARDI_aggregated','SE_line','SE_transformer','SE','SALOF_transformer','SOG']
        self.CoordinateFilePath  = os.path.join(self.Settings['Project Path'],self.Settings['Active Project'], 'CoordinateCSVFiles')
        self.DataPath = os.path.join(self.Settings['Project Path'],self.Settings['Active Project'], DataFolderName)


        self.SystemLevelData()
        self.SystemLevelTimeSeriesData()
        self.ProcessLineCoordinates()
        self.ProcessAssetLevelMetric()

    def ProcessAssetLevelMetric(self):

        # Process for Asset Level Metrics and PV coordinates(this is yet not used in dashboard)
        self.AssetMetricsTimeSeries, self.PVcoordinates, self.AssetMetricsAggregated = {}, {},{}

        for folder in os.listdir(self.DataPath):
            self.AssetMetricsTimeSeries[folder],self.AssetMetricsAggregated[folder] = {},{}
            for metric in self.AssetLevelMetrics:
                self.AssetMetricsAggregated[folder][metric] = ReadFromFile(os.path.join(self.DataPath,folder,metric+'Asset.csv'))
                self.AssetMetricsTimeSeries[folder][metric] = ReadFromFile(os.path.join(self.DataPath,folder,metric+'AssetTimeSeries.csv'))
                self.PVcoordinates[folder] = self.ConvertCoordinates(ReadFromFile(os.path.join(self.CoordinateFilePath,folder.replace('-customer','customer')+'.csv')))

        # Convert coordinates into
        self.TransformerCoordinatesDict = self.ConvertCoordinates(ReadFromFile(os.path.join(self.CoordinateFilePath,'transformer_coords.csv')))
        self.NodeCoordinatesDict = self.ConvertCoordinates(ReadFromFile(os.path.join(self.CoordinateFilePath,'node_coords.csv')))
        self.CustomerCoordinatesDict = self.ConvertCoordinates(ReadFromFile(os.path.join(self.CoordinateFilePath,'customer_coords.csv')))



    def ConvertCoordinates(self,DataFrame):
        
        DataDict = {}
        for index in range(len(DataFrame)):
            Data = DataFrame.loc[index]
            DataDict[Data['component_name']] = {}
            DataDict[Data['component_name']]['x'],DataDict[Data['component_name']]['y'] = self.lat_long_converter(Data['x'],Data['y'])
        return DataDict

    def ProcessLineCoordinates(self):

        
        LineCoordinateData = ReadFromFile(os.path.join(self.CoordinateFilePath,'line_coords.csv'))
        self.x_lines, self.y_lines = [],[]
        self.initial_x, self.initial_y = [],[]
        self.LineCoordintesDict = {}

        for index in range(len(LineCoordinateData)):
            line_data = LineCoordinateData.loc[index]
            Start_x, Start_y = self.lat_long_converter(line_data['x1'],line_data['y1'])
            End_x, End_y = self.lat_long_converter(line_data['x2'],line_data['y2'])

            self.initial_x.extend([Start_x,End_x])
            self.initial_y.extend([Start_y, End_y])

            self.x_lines.extend([Start_x,End_x,None])
            self.y_lines.extend([Start_y,End_y,None])

            self.LineCoordintesDict[line_data['component_name']] = {}
            self.LineCoordintesDict[line_data['component_name']]['x'],self.LineCoordintesDict[line_data['component_name']]['y']=(Start_x+End_x)/2,(Start_y+End_y)/2


        self.initial_x, self.initial_y = (max(self.initial_x)+min(self.initial_x))/2, (max(self.initial_y)+min(self.initial_y))/2

    def lat_long_converter(self,x1, y1):
        inProj = Proj(init='epsg:32644')
        outProj = Proj(init='epsg:4326')
        x2, y2 = transform(inProj, outProj, x1, y1)
        return y2, x2

    def SystemLevelTimeSeriesData(self):

        self.SystemLevelMetricsTimeSeries = {}
        for folder in os.listdir(self.DataPath):

            self.SystemLevelMetricsTimeSeries[folder] = {'TimeStamp':[], 'SARDI_voltage':[],'SARDI_line':[], 'SARDI_transformer':[],'SARDI_aggregated':[],'SE_line':[],'SE_transformer':[],'SE':[],'SALOF_transformer':[],'SOG':[]}

            MetricData = ReadFromFile(os.path.join(self.DataPath, folder, 'SystemLevelMetricsTimeSeries.csv'))
            for keys in self.SystemLevelMetricsTimeSeries[folder].keys():
                self.SystemLevelMetricsTimeSeries[folder][keys] = list(MetricData[keys])

         
            # Hard coded to convert into percentage (Remove later)
            for metric in ['SARDI_voltage', 'SARDI_line', 'SARDI_transformer', 'SARDI_aggregated']:
                tempdata = self.SystemLevelMetricsTimeSeries[folder][metric]
                converteddata = [val * 100 / self.Settings['ClassicalPVTotalSimulationMinute'] for val in tempdata] if self.TypePV == 'Classical' else [val * 100 / self.Settings['AdvancedPVTotalSimulationMinute'] for val in tempdata]
                self.SystemLevelMetricsTimeSeries[folder][metric] = converteddata

            self.SystemLevelMetricsTimeSeries[folder]['SOG'] = [val / (self.Settings['ClassicalPVMWh']*60*10/self.Settings['Time Step (min)']) for val in self.SystemLevelMetricsTimeSeries[folder]['SOG']] if self.TypePV == 'Classical' else [val / (self.Settings['AdvancedPVMWh']*60*10/self.Settings['Time Step (min)']) for val in self.SystemLevelMetricsTimeSeries[folder]['SOG']]
            for metric in ['SE_line', 'SE_transformer', 'SE']:
                self.SystemLevelMetricsTimeSeries[folder][metric] = [100 - val for val in self.SystemLevelMetricsTimeSeries[folder][metric]]
            # Hard coded upt this to convert into percentage (Remove later)

            self.SystemLevelMetricsTimeSeries[folder]['SALOF_transformer'] = [min(val, 100) for val in self.SystemLevelMetricsTimeSeries[folder]['SALOF_transformer']]
            # Convert date time string into datetime
            self.SystemLevelMetricsTimeSeries[folder]['TimeStamp'] = [datetime.strptime(val,'%Y-%m-%d %H:%M:%S') for val in self.SystemLevelMetricsTimeSeries[folder]['TimeStamp']]


    def SystemLevelData(self):

        
        self.SystemLevelMetrics = {'Scenarios':[], 'x_val':[], 'SARDI_voltage':[],'SARDI_line':[], 'SARDI_transformer':[],'SARDI_aggregated':[],'SE_line':[],'SE_transformer':[],'SE':[],'SALOF_transformer':[],'SOG':[]}
        
        self.Scenarios = [folder for folder in os.listdir(self.DataPath)]
        for folder in os.listdir(self.DataPath):

            scenario = folder.split('-')[0] + '-' + folder.split('-')[2] if folder !='Base' else folder
            self.SystemLevelMetrics['Scenarios'].append(scenario)

            x = 0 if folder=='Base' else float(folder.split('%')[0])
            self.SystemLevelMetrics['x_val'].append(x)

            # Read systemlevelmetrics.csv
            MetricData = ReadFromFile(os.path.join(self.DataPath,folder,'SystemLevelMetrics.csv'))
            MetricDataDict = dict(zip(list(MetricData['Metrics']),list(MetricData['Values'])))
            for Metric, Values in MetricDataDict.items():
                self.SystemLevelMetrics[Metric].append(Values)

        # Now let's sort all the values
        for keys, values in self.SystemLevelMetrics.items():
            if keys!='x_val':
                sortedx,sortedvalue = zip(*sorted(zip(self.SystemLevelMetrics['x_val'],values)))
                self.SystemLevelMetrics[keys] = sortedvalue
        self.SystemLevelMetrics['x_val'] = sortedx

        # Hard coded to convert into percentage (Remove later)
        for metric in ['SARDI_voltage','SARDI_line','SARDI_transformer','SARDI_aggregated']:
            tempdata = self.SystemLevelMetrics[metric]
            converteddata = [val * 100 / self.Settings['ClassicalPVTotalSimulationMinute'] for val in
                             tempdata] if self.TypePV == 'Classical' else [
                val * 100 / self.Settings['AdvancedPVTotalSimulationMinute'] for val in tempdata]

            self.SystemLevelMetrics[metric] = converteddata

        self.SystemLevelMetrics['SOG']  = [val/(self.Settings['ClassicalPVMWh']*60*10/self.Settings['Time Step (min)']) for val in self.SystemLevelMetrics['SOG']] if self.TypePV == 'Classical' else [val/(self.Settings['AdvancedPVMWh']*60*10/self.Settings['Time Step (min)']) for val in self.SystemLevelMetrics['SOG']]
        for metric in ['SE_line','SE_transformer','SE']:
            self.SystemLevelMetrics[metric] = [100-val for val in self.SystemLevelMetrics[metric]]
        # Hard coded upto this to convert into percentage (Remove later)
        
        self.SystemLevelMetrics['SALOF_transformer'] =  [val if val<100 else None for val in self.SystemLevelMetrics['SALOF_transformer']]#[min(val,100) for val in self.SystemLevelMetrics['SALOF_transformer']]


        ViolationMetrics = ['Scenarios', 'x_val','SARDI_voltage','SARDI_line','SARDI_transformer','SARDI_aggregated']
        Efficiency = ['Scenarios', 'x_val','SE_line','SE_transformer','SE']
        LossOfLife  =['Scenarios', 'x_val','SALOF_transformer']
        Overgeneration=['Scenarios', 'x_val','SOG']

        self.ViolationDict, self.Efficiency, self.Lossoflife, self.overgeneration = {},{},{},{}

        for metric in ViolationMetrics:
            self.ViolationDict[metric] = self.SystemLevelMetrics[metric]

        for metric in Efficiency:
            self.Efficiency[metric] = self.SystemLevelMetrics[metric]

        for metric in LossOfLife:
            self.Lossoflife[metric] = self.SystemLevelMetrics[metric]

        for metric in Overgeneration:
            self.overgeneration[metric] = self.SystemLevelMetrics[metric]

