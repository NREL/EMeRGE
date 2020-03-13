import pandas as pd
import os

class ProcessExport:

    def __init__(self, ExportObject, ExportPath):

        self.system_level_metrics = ExportObject.system_level_metrics
        self.system_level_metrics_time_series = ExportObject.system_level_metrics_time_series
        self.Asset_level_metric = ExportObject.Asset_level_metric
        self.Asset_level_metric_time_series = ExportObject.Asset_level_metric_time_series
        self.AssetLevelParameters = ExportObject.AssetLevelParameters

        # Export system level metrics
        if not os.path.exists(ExportPath): os.mkdir(ExportPath)
        DataToBeExported  = {'Metrics':[], 'Values':[]}
        DataToBeExported['Metrics'], DataToBeExported['Values'] = [keys for keys in self.system_level_metrics.keys()], [values for keys,values in self.system_level_metrics.items()]
        self.CSVexport(DataToBeExported,os.path.join(ExportPath, 'SystemLevelMetrics.csv'))

        # Export system level time series metrics
        self.CSVexport(self.system_level_metrics_time_series, os.path.join(ExportPath, 'SystemLevelMetricsTimeSeries.csv'))

        # Export asset level metrics
        for keys,values in self.Asset_level_metric.items():
            DataToBeExported = {'Metrics': [], 'Values': []}
            DataToBeExported['Metrics'], DataToBeExported['Values'] = [key for key in values.keys()], [value for key, value in values.items()]
            self.CSVexport(DataToBeExported, os.path.join(ExportPath,keys+'Asset.csv'))

        # Export asset level time series metrics
        for keys, values in self.Asset_level_metric_time_series.items():
            self.CSVexport(values, os.path.join(ExportPath,keys+'AssetTimeSeries.csv'))

        # export electrical parameters
        for keys, values in self.AssetLevelParameters.items():
            self.CSVexport(values, os.path.join(ExportPath, keys + 'AssetTimeSeries.csv'))

    # Function for wrriting dictionary into CSV file
    def CSVexport(self,DataDict, ExportPath):
        Dataframe = pd.DataFrame.from_dict(DataDict)
        Dataframe.to_csv(ExportPath,index=False)


