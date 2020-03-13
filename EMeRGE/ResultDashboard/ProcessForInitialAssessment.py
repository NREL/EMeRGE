import os
import pandas as pd
from datetime import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt

class ProcessLoadProfile:

    def __init__(self, DashboardSettings, FolderName='InitialAssessment'):

        self.DashboardSettings = DashboardSettings
        self.Folder = FolderName
        self.ReadAllFiles()

        self.CustomersDataFrameGrouped = self.ConsumerData.groupby('cust_type').sum()['kw'].to_dict()
        self.CustomersTimeSeries, self.CustomersTimeSeriesbyType = [], {}
        for customertype, totalload in self.CustomersDataFrameGrouped.items():
            self.CustomersTimeSeriesbyType[customertype] = [puload*totalload for puload in self.DataFrameDict[customertype]]
            if self.CustomersTimeSeries == []:
                self.CustomersTimeSeries = self.CustomersTimeSeriesbyType[customertype]
            else:
                self.CustomersTimeSeries = [sum(x) for x in zip(self.CustomersTimeSeries, self.CustomersTimeSeriesbyType[customertype])]

        self.PeakCapacity = max(self.CustomersTimeSeries)
        self.PeakIndex = self.CustomersTimeSeries.index(self.PeakCapacity)

    def GetDataDict(self, PVpercen, DateString):
        self.CustomersTimeSeriesbyTypeForPV, self.CustomersTimeSeriesForPV = {},[]
        for customertype, totalload in self.CustomersDataFrameGrouped.items():
            self.CustomersTimeSeriesbyTypeForPV[customertype] = [self.DataFrameDict[customertype][index]*totalload - totalload*self.DataFrameDict[customertype][self.PeakIndex]*(PVpercen/100)*self.SolarData[index] for index in range(len(self.DataFrameDict[customertype]))]
            if self.CustomersTimeSeriesForPV == []:
                self.CustomersTimeSeriesForPV = self.CustomersTimeSeriesbyTypeForPV[customertype]
                PVgeneration = [totalload*self.DataFrameDict[customertype][self.PeakIndex]*(PVpercen/100)*self.SolarData[index] for index in range(len(self.DataFrameDict[customertype]))]
            else:
                self.CustomersTimeSeriesForPV = [sum(x) for x in zip(self.CustomersTimeSeriesForPV, self.CustomersTimeSeriesbyTypeForPV[customertype])]
                PVgeneration = [sum(x) for x in zip(PVgeneration,[totalload*self.DataFrameDict[customertype][self.PeakIndex]*(PVpercen/100)*self.SolarData[index] for index in range(len(self.DataFrameDict[customertype]))])]

        self.CustomersTimeSeriesbyTypeForPVSorted = {}
        SortedTimeSeriesLoadProfile, IDs = zip(*sorted(zip(self.CustomersTimeSeriesForPV, range(len(self.CustomersTimeSeriesForPV))), reverse=True))
        for loadtype, loadlist in self.CustomersTimeSeriesbyTypeForPV.items():
            self.CustomersTimeSeriesbyTypeForPVSorted[loadtype] = [loadlist[index] for index in IDs]


        # Find out a day for which plot is needed
        dayindex = dt.strptime(DateString.split(' ')[0],'%Y-%m-%d').timetuple().tm_yday
        date = dt.strptime(DateString.split(' ')[0],'%Y-%m-%d')
        year, month, day = date.year, date.month, date.day

        lengthofdata = int(1440/self.DashboardSettings['Time Step (min)'])

        xdatelist = [dt(year,month,day) + timedelta(minutes=self.DashboardSettings['Time Step (min)']*i) for i in range(lengthofdata)]
        DailyProfile = {'TimeStamp': xdatelist}
        for keys, values in self.CustomersTimeSeriesbyTypeForPV.items():
            DailyProfile[keys] = values[(dayindex-1)*lengthofdata:(dayindex)*lengthofdata]
        self.CustomersTimeSeriesbyTypeForPVSorted['TimeStamp'] = [index * 100 / len(self.CustomersTimeSeriesForPV) for index
                                                            in range(len(self.CustomersTimeSeriesForPV))]
        # Dataframe for statistics

        AbsoluteLoad = [abs(value) for value in self.CustomersTimeSeriesForPV]
        max_net_gen = 'NA' if PVpercen==0 else -round(min(self.CustomersTimeSeriesForPV)/1000,2)
        load_factor = sum(self.CustomersTimeSeriesForPV)/(len(self.CustomersTimeSeriesForPV)*max(self.CustomersTimeSeriesForPV))


        RowNames = ['Peak load (MW)','Minimum load (MW)', 'Maximum solar generation (MW)', 'Maximmum Net Generation (MW)', 'Annual load factor']
        RowValues = [round(max(self.CustomersTimeSeriesForPV)/1000,2),round(min(AbsoluteLoad)/1000,2),round(max(PVgeneration)/1000,2),max_net_gen, load_factor]
        RowIndex = [self.CustomersTimeSeriesForPV.index(max(self.CustomersTimeSeriesForPV)), AbsoluteLoad.index(min(AbsoluteLoad)),PVgeneration.index(max(PVgeneration)),self.CustomersTimeSeriesForPV.index(min(self.CustomersTimeSeriesForPV)),'NA']
        for id,value in enumerate(RowIndex):
            RowIndex[id] = (dt(2018,1,1) + timedelta(minutes=value*self.DashboardSettings['Time Step (min)'])).strftime('%Y-%m-%d %H:%M:%S') if value != 'NA' else 'NA'

        DataFrameStatistics = pd.DataFrame({'Parameters': RowNames,'Value': RowValues, 'Time': RowIndex})

        # Sampling to show few data points
        SampledLoadDurationData = {}
        for keys,values in self.CustomersTimeSeriesbyTypeForPVSorted.items():
            SampledLoadDurationData[keys] = [values[index] for index in range(0,len(values),35)]

        return  SampledLoadDurationData, DailyProfile, DataFrameStatistics


    def ReadAllFiles(self):

        FilePath = os.path.join(self.DashboardSettings['Project Path'],self.DashboardSettings['Active Project'],self.Folder)
        FileDict = {'residential':'residential.csv','commercial':'commercial.csv','industrial':'industrial.csv', 'agricultural':'agricultural.csv'}
        self.DataFrameDict  = {}

        for consumertype, filename in FileDict.items():
            self.DataFrameDict[consumertype] = list(pd.read_csv(os.path.join(FilePath,filename),header=None)[0])
        self.ConsumerData =  pd.read_csv(os.path.join(FilePath,'consumer.csv'))
        self.SolarData = list(pd.read_csv(os.path.join(FilePath,'solarmult.csv'),header=None)[0])


if __name__ == '__main__':
    DashboardSettings = {"Project Path" : "C:\\Users\\KDUWADI\\Desktop\\NREL_Projects\\CIFF-TANGEDCO\\TANGEDCO\\SoftwareTools\\VisualizingInDashboard\\Projects",
                         "Active Project" : "GWC",
                         'Time Step (min)' : 15}
    a = ProcessLoadProfile(DashboardSettings)
    CustomersTimeSeriesbyTypeForPV, DailyProfile, DataFrameStatistics = a.GetDataDict(50,'2018-1-1')


