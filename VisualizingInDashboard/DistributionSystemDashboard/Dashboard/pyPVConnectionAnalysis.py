"""
author : kapil duwadi
version: 0.0.1
"""

import os
import shutil
import math
from datetime import timedelta
from datetime import datetime as dt
from Dashboard.DateTimeProcessingContainer import *
from Dashboard.DSSRiskAnalyzer.pyRisk import *
from ReadersContainer import *
import toml

class PVConnection:

    def __init__(self, SettingsFile, PVDict, TimeDict,Accept):

        self.Settings = SettingsFile
        self.PVDict = PVDict
        self.TimeDict = TimeDict
        self.Accept = Accept
        self.CreateNewDSSFile()

    def ProcessResult(self):

        ExportPath = os.path.join(self.ProjectPath,self.Settings['Active Project'],'Exports','category')
        self.AssetLevelMetrics = ['NVRI', 'LVRI', 'TVRI', 'CRI', 'TE', 'LE', 'TLOF', 'TOG']
        self.SystemMetrics = ['SARDI_voltage', 'SARDI_line', 'SARDI_transformer', 'SARDI_aggregated', 'SE_line',
                              'SE_transformer', 'SE', 'SALOF_transformer', 'SOG']

        BaseData = ReadFromFile(os.path.join(ExportPath,'Base', 'SystemLevelMetrics.csv'))
        BaseDataDict = dict(zip(list(BaseData['Metrics']), list(BaseData['Values'])))
        NewData = ReadFromFile(os.path.join(ExportPath,'Temporary', 'SystemLevelMetrics.csv'))
        NewDataDict = dict(zip(list(NewData['Metrics']), list(NewData['Values'])))
        RiskMetricDiff = (NewDataDict['SARDI_aggregated'] - BaseDataDict['SARDI_aggregated'])/(14.4)
        OvergenerationDiff = (NewDataDict['SOG'] - BaseDataDict['SOG'])/(12*24*4)
        EnergyLossDiff = (NewDataDict['SE']-BaseDataDict['SE'])

        return RiskMetricDiff, OvergenerationDiff,EnergyLossDiff

    def ProcessForDifferenceinParameters(self):

        ExportPath = os.path.join(self.ProjectPath, self.Settings['Active Project'], 'Exports', 'category')

        voltageBase = ReadFromFile(os.path.join(ExportPath,'Base','voltagemagAssetTimeSeries.csv'))
        lineBase = ReadFromFile(os.path.join(ExportPath, 'Base', 'lineloadingAssetTimeSeries.csv'))
        transformerBase = ReadFromFile(os.path.join(ExportPath, 'Base', 'transformerloadingAssetTimeSeries.csv'))

        voltageTemporary = ReadFromFile(os.path.join(ExportPath, 'Temporary', 'voltagemagAssetTimeSeries.csv'))
        lineTemporary = ReadFromFile(os.path.join(ExportPath, 'Temporary', 'lineloadingAssetTimeSeries.csv'))
        transformerTemporary = ReadFromFile(os.path.join(ExportPath, 'Temporary', 'transformerloadingAssetTimeSeries.csv'))


        voltageDiffDict, voltageDict = {}, {}
        for columnname in list(voltageBase.columns):
            Difference= [x[1]-x[0] for x in zip(list(voltageBase[columnname]),list(voltageTemporary[columnname]))]
            voltageDiffDict[columnname] = max(Difference)
            voltageDict[columnname] = voltageBase[columnname].tolist()[Difference.index(max(Difference))]


        lineDiffDict,lineDict = {}, {}
        for columnname in list(lineBase.columns):
            Difference = [x[1] - x[0] for x in zip(list(lineBase[columnname]), list(lineTemporary[columnname]))]
            lineDiffDict[columnname] = max(Difference)
            lineDict[columnname] = lineBase[columnname].tolist()[Difference.index(max(Difference))]

        transformerDiffDict,transformerDict  = {},{}
        for columnname in list(transformerBase.columns):
            Difference = [x[1] - x[0] for x in zip(list(transformerBase[columnname]), list(transformerTemporary[columnname]))]
            transformerDiffDict[columnname] = max(Difference)
            transformerDict[columnname] = transformerBase[columnname].tolist()[Difference.index(max(Difference))]

        '''
        voltageBaseDict, lineBaseDict, transformerBaseDict = dict(zip(voltageBase['Metrics'],voltageBase['Values'])), dict(zip(lineBase['Metrics'],lineBase['Values'])), dict(zip(transformerBase['Metrics'],transformerBase['Values']))
        voltageTemporaryDict, lineTemporaryDict, transformerTemporaryDict = dict(
            zip(voltageTemporary['Metrics'], voltageTemporary['Values'])), dict(
            zip(lineTemporary['Metrics'], lineTemporary['Values'])), dict(
            zip(transformerTemporary['Metrics'], transformerTemporary['Values']))

        voltageDiffDict = {keys: voltageTemporaryDict[keys] - values for keys,values in voltageBaseDict.items()}
        lineDiffDict = {keys: lineTemporaryDict[keys] - values for keys, values in lineBaseDict.items()}
        transformerDiffDict = {keys: transformerTemporaryDict[keys] - values for keys, values in transformerBaseDict.items()}
        '''

        return voltageDiffDict, lineDiffDict, transformerDiffDict,voltageDict, lineDict, transformerDict

    def CreateNewDSSFile(self):

        self.WorkingPath = os.path.join(self.Settings['Project Path'],self.Settings['Active Project'],'PVConnection')

        self.ProjectPath  = os.path.join(self.Settings['Project Path'],self.Settings['Active Project'],'PVConnection','Projects')
        if os.path.exists(self.ProjectPath): shutil.rmtree(self.ProjectPath)

        if not os.path.exists(os.path.join(self.WorkingPath,'Temporary')): os.mkdir(os.path.join(self.WorkingPath,'Temporary'))

        # Copy all the files from 'Base' folder to 'Temporary' folder
        for file in os.listdir(os.path.join(self.WorkingPath,'Base')):
            shutil.copy(os.path.join(self.WorkingPath,'Base',file),os.path.join(self.WorkingPath,'Temporary'))

        self.AddPVSystem(os.path.join(self.WorkingPath,'Temporary'),'load.dss','PVsystem.dss',self.PVDict)

        # Now perform openDSS simulation

        self.RunPowerFlow()

    def RunPowerFlow(self):

        [Hour, Minute, Second]= self.TimeDict['Time'].split(':')
        Hour,Minute,Second = int(float(Hour)),int(float(Minute)),int(float(Second))

        Day =  dt.strptime(self.TimeDict['Day'].split(' ')[0], '%Y-%m-%d')
        startdate = dt(Day.year,Day.month,Day.day,Hour,Minute,Second)
        if self.TimeDict['Mode'] == 'Snapshot':
            enddate = startdate+timedelta(minutes=self.Settings['Time Step (min)'])
            aggregate_time = self.Settings['Time Step (min)']


        if self.TimeDict['Mode'] == 'Daily':
            enddate = startdate+timedelta(hours=24)
            aggregate_time = self.Settings['Time Step (min)']


        Month = Day.month + 1 if Day.month <12 else 1
        if self.TimeDict['Mode'] == 'Monthly':
            enddate = dt(Day.year,Month,Day.day,Hour,Minute,Second)
            aggregate_time = 1440

        if self.TimeDict['Mode'] == 'Yearly':
            startdate = dt(Day.year,1,1,0,0,0)
            enddate = dt(Day.year,12,31,23,59,59)
            aggregate_time = 1440

        os.makedirs(os.path.join(self.ProjectPath,self.Settings['Active Project']))
        shutil.copytree(os.path.join(self.WorkingPath,'ExtraData'),os.path.join(self.ProjectPath,self.Settings['Active Project'],'ExtraData'))
        os.mkdir(os.path.join(self.ProjectPath,self.Settings['Active Project'],'Exports'))
        os.mkdir(os.path.join(self.ProjectPath, self.Settings['Active Project'], 'DSSScenarios'))
        shutil.copytree(os.path.join(self.WorkingPath,'Base'),os.path.join(self.ProjectPath,self.Settings['Active Project'],'DSSScenarios','Base'))
        shutil.copytree(os.path.join(self.WorkingPath, 'Temporary'),os.path.join(self.ProjectPath, self.Settings['Active Project'], 'DSSScenarios','Temporary'))
        os.makedirs(os.path.join(self.ProjectPath, self.Settings['Active Project'], 'AnalysisScenarios','Category'))

        BaseSettingsDict = ReadFromFile(os.path.join(self.WorkingPath,'settings.toml'))
        BaseSettingsDict['Project path'] = self.ProjectPath
        BaseSettingsDict['Active_Scenario'] = 'category'
        BaseSettingsDict['start_time'] = dt.strftime(startdate,"%Y/%m/%d %H:%M:%S")
        BaseSettingsDict['stop_time'] = dt.strftime(enddate, "%Y/%m/%d %H:%M:%S")
        BaseSettingsDict['Risk_metric_aggregate_minutes'] = aggregate_time
        TomlStrings = toml.dumps(BaseSettingsDict)
        TextFile = open(os.path.join(self.ProjectPath, self.Settings['Active Project'], 'AnalysisScenarios','Category', 'settings.toml'), "w")
        TextFile.write(TomlStrings)
        TextFile.close()

        # Run risk analysis
        RunRiskAnalysis(os.path.join(self.ProjectPath, self.Settings['Active Project'], 'AnalysisScenarios','Category','settings.toml'))

    def AddPVSystem(self, RootPath, LoadDSS, PVDSS, PVdict):

        Phases = 1 if PVdict['Phases'] != 'RYB' else 3
        Phase2NumDict = {"R":1,"Y":2,"B":3}
        LineToAdd = ['new',
                     'pvsystem.{}'.format(PVdict['LoadName']),
                     'irradiance={}'.format(PVdict['Irradiance']),
                     'kva={}'.format(float(PVdict['Capacity']*PVdict['InverterOverSizeFactor'])),
                     'pmpp={}'.format(float(PVdict['Capacity'])),
                     'kvar={}'.format(PVdict['KVAR']),
                     '%cutin={}'.format(PVdict['CutIn']),
                     '%cutout={}'.format(PVdict['CutOut']),
                     'yearly={}'.format(PVdict['Profile'])]

        with open(os.path.join(RootPath,LoadDSS)) as fp:

            readline = fp.readline()

            while readline:

                linecontent = str(readline.strip())
                if PVdict['LoadName'].lower() in linecontent.lower():
                    linecontentlist = linecontent.split(' ')
                    for element in linecontentlist:
                        if 'bus1=' in element:
                            Bus1string = element
                        if 'kv=' in element:
                            kvstring= element
                        if 'phases=' in element:
                            phasestring = element
                    break

                readline = fp.readline()
        fp.close()
        if Phases>=float(phasestring.split('=')[1]):
            LineToAdd.append(Bus1string)
            LineToAdd.append(phasestring)
            LineToAdd.append(kvstring)

        if Phases < float(phasestring.split('=')[1]):
            LineToAdd.append(Bus1string.split('.')[0]+'.'+Phase2NumDict[PVdict['Phases']]+'.0')
            LineToAdd.append('phase={}'.format(Phases))
            LineToAdd.append('kv={}'.format(float(kvstring.split('=')[1])/math.sqrt(3)))


        LineString = ' '.join(LineToAdd)

        newfile = open(os.path.join(RootPath,PVDSS), "w")
        newfile.write(LineString)
        newfile.close()

if __name__ == "__main__":

    SettingsFile  = ReadFromFile(r"C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\VisualizingInDashboard\Projects\settings.toml")
    PVDict = {'LoadName':'gwclt12', 'Irradiance':0.98,'Capacity':5,'InverterOverSizeFactor':0.9,'KVAR':0,'CutIn':0.05,'CutOut':0.05,'Profile':'solarmult','Phases':'RYB'}
    TimeDict = {'Mode':'Daily','Time':'5:00:00','Day':'2018-1-1 0:0:0'}
    a = PVConnection(SettingsFile,PVDict,TimeDict)
    b,c,d = a.ProcessForDifferenceinParameters()
    print(b)
    print(c)
    print(d)

