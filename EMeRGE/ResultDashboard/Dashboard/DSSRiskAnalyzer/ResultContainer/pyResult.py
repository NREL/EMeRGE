from ResultDashboard.Dashboard.DSSRiskAnalyzer.MetricContainer.pyMetric import *
class ResultProcessor:

    def __init__(self,*argv):

        # Extract all the values
        [TimeStampForRecordingData, NodeMetricDict,LineMetricDict,TransformerMetricDict,SystemMetricDict,TemperatureData,TransformerLifePrameters] = argv

        # Define container dict for all results to be exported
        SystemLevelMetrics = ['SARDI_voltage', 'SARDI_line', 'SARDI_transformer', 'SARDI_aggregated', 'SE_line', 'SE_transformer', 'SE', 'SALOF_transformer','SOG']
        self.system_level_metrics = {Metric:[] for Metric in SystemLevelMetrics}

        ColNamesForTimeSeriesSystemLevelMetrics = ['TimeStamp'] + SystemLevelMetrics
        self.system_level_metrics_time_series  ={Column: [] for Column in ColNamesForTimeSeriesSystemLevelMetrics }

        AssetLevelMetrics = ['NVRI','LVRI','CRI','LE','TE','TLOF','TOG']
        self.Asset_level_metric  ={Metric: {} for Metric in AssetLevelMetrics}
        self.Asset_level_metric_time_series = {}

        AsssetLevelParameters = ['voltagemag','lineloading','transformerloading']
        self.AssetLevelParameters = {Metric: {} for Metric in AsssetLevelParameters}

        self.AssetLevelParameters['voltagemag'] = self.ProcessAssetLevelParameters([NodeMetricDict[TimeStamp]['VoltageMag'] for TimeStamp in NodeMetricDict.keys()], TimeStampForRecordingData)
        self.AssetLevelParameters['lineloading'] = self.ProcessAssetLevelParameters(
            [LineMetricDict[TimeStamp]['PULoading'] for TimeStamp in LineMetricDict.keys()], TimeStampForRecordingData)
        self.AssetLevelParameters['transformerloading'] = self.ProcessAssetLevelParameters(
            [TransformerMetricDict[TimeStamp]['PULoading'] for TimeStamp in TransformerMetricDict.keys()], TimeStampForRecordingData)


        # Compute for system level metrics
        self.system_level_metrics_time_series['TimeStamp'] = TimeStampForRecordingData

        self.system_level_metrics['SARDI_voltage'], self.system_level_metrics_time_series['SARDI_voltage'] = self.ProcessSequence([NodeMetricDict[TimeStamp]['SARDI'] for TimeStamp in NodeMetricDict.keys()],TimeStampForRecordingData)

        self.system_level_metrics['SARDI_line'], self.system_level_metrics_time_series['SARDI_line'] = self.ProcessSequence([LineMetricDict[TimeStamp]['SARDI'] for TimeStamp in LineMetricDict.keys()],TimeStampForRecordingData)

        self.system_level_metrics['SARDI_transformer'], self.system_level_metrics_time_series['SARDI_transformer'] = self.ProcessSequence([TransformerMetricDict[TimeStamp]['SARDI'] for TimeStamp in TransformerMetricDict.keys()],TimeStampForRecordingData)

        self.system_level_metrics['SARDI_aggregated'], self.system_level_metrics_time_series['SARDI_aggregated'] = self.ProcessSequence([SystemMetricDict[TimeStamp]['SARDI'] for TimeStamp in SystemMetricDict.keys()],TimeStampForRecordingData)

        self.system_level_metrics['SE_line'], self.system_level_metrics_time_series['SE_line'] = self.ProcessForEfficiency([SystemMetricDict[TimeStamp]['LineLossPower'] for TimeStamp in SystemMetricDict.keys()],TimeStampForRecordingData,[0,2])

        self.system_level_metrics['SE_transformer'], self.system_level_metrics_time_series['SE_transformer'] = self.ProcessForEfficiency([SystemMetricDict[TimeStamp]['TransformerLossPower'] for TimeStamp in SystemMetricDict.keys()],TimeStampForRecordingData, [0, 2])

        self.system_level_metrics['SE'], self.system_level_metrics_time_series['SE'] = self.ProcessForEfficiency([SystemMetricDict[TimeStamp]['TotalLossPower'] for TimeStamp in SystemMetricDict.keys()],TimeStampForRecordingData, [0, 2])

        self.system_level_metrics['SOG'], self.system_level_metrics_time_series['SOG'] = self.ProcessSequence([SystemMetricDict[TimeStamp]['Overgeneration'] for TimeStamp in SystemMetricDict.keys()],TimeStampForRecordingData)

        # Compute Asset level metrics

        self.Asset_level_metric['NVRI'], self.Asset_level_metric_time_series['NVRI'] = self.ProcessListofDict([NodeMetricDict[TimeStamp]['VRI'] for TimeStamp in NodeMetricDict.keys()], TimeStampForRecordingData)

        self.Asset_level_metric['LVRI'], self.Asset_level_metric_time_series['LVRI']  = self.ProcessListofDict([LineMetricDict[TimeStamp]['VRI'] for TimeStamp in LineMetricDict.keys()], TimeStampForRecordingData)

        self.Asset_level_metric['TVRI'], self.Asset_level_metric_time_series['TVRI']  = self.ProcessListofDict([TransformerMetricDict[TimeStamp]['VRI'] for TimeStamp in TransformerMetricDict.keys()], TimeStampForRecordingData)

        self.Asset_level_metric['TOG'], self.Asset_level_metric_time_series['TOG'] = self.ProcessListofDict([TransformerMetricDict[TimeStamp]['Overgeneration'] for TimeStamp in TransformerMetricDict.keys()], TimeStampForRecordingData)

        self.Asset_level_metric['CRI'], self.Asset_level_metric_time_series['CRI'] = self.ProcessListofDict([SystemMetricDict[TimeStamp]['CRI_weight'] for TimeStamp in SystemMetricDict.keys()],TimeStampForRecordingData)

        self.Asset_level_metric['LE'], self.Asset_level_metric_time_series['LE'] = self.ProcessListOfDictforEfficiecny([LineMetricDict[TimeStamp]['EfficiencyMetric'] for TimeStamp in LineMetricDict.keys()],TimeStampForRecordingData,[2,4])

        self.Asset_level_metric['TE'], self.Asset_level_metric_time_series['TE'] = self.ProcessListOfDictforEfficiecny([TransformerMetricDict[TimeStamp]['EfficiencyMetric'] for TimeStamp in TransformerMetricDict.keys()],TimeStampForRecordingData, [2, 4])

        self.Asset_level_metric['TLOF'], self.Asset_level_metric_time_series['TLOF'] = self.ProcessTransformerLoadingListofDict([TransformerMetricDict[TimeStamp]['PULoading'] for TimeStamp in TransformerMetricDict.keys()],TimeStampForRecordingData,TemperatureData,TransformerLifePrameters)

        self.system_level_metrics['SALOF_transformer'] = sum([val for key, val in self.Asset_level_metric['TLOF'].items()]) / len(self.Asset_level_metric['TLOF'].keys())

        self.system_level_metrics_time_series['SALOF_transformer'] = [sum(array) / len(self.Asset_level_metric.keys()) for array in zip(*[self.Asset_level_metric_time_series['TLOF'][key] for key in self.Asset_level_metric['TLOF'].keys()])]


    def ProcessAssetLevelParameters(self, ListOfDict, ListofTimeStamps):

        Temporary_Dict = {keys: [] for keys in ListOfDict[0].keys()}
        for keys in ListOfDict[0].keys():
            Temporary_Dict[keys] = [Dict[keys] for Dict in ListOfDict]
        return Temporary_Dict

    def ProcessTransformerLoadingListofDict(self,ListOfDict, ListofTimeStamps,TemperatureData,TransformerLifePrameters):

        # Process List of Dict of transformer loading to compute loss of life
        ListOfKeys = ['TimeStamp'] + [keys for keys in ListOfDict[0].keys()]

        TemporaryDict, TemporaryDictList = {keys: [] for keys in ListOfDict[0].keys()}, {keys: [] for keys in ListOfKeys}

        TemporaryDictList['TimeStamp'] = ListofTimeStamps

        for keys in TemporaryDict.keys():
            TemporaryDict[keys], TemporaryDictList[keys] = self.LossOfLifeFromLoading([Dictionary[keys] for Dictionary in ListOfDict],TemperatureData,TransformerLifePrameters,ListofTimeStamps)

        return TemporaryDict, TemporaryDictList

    def LossOfLifeFromLoading(self,TransformerLoading,TemperatureData,TransformerLifeParameters, ListofTimeStamps):

        # Computes loss of life for all transformers both scalar and timeseries

        SizeOfSplit = int(len(TransformerLoading) / len(ListofTimeStamps))

        TransformerLoadingSplitted = [TransformerLoading[i:i+SizeOfSplit] for i in range(0, len(TransformerLoading), SizeOfSplit)]
        TemperatureDataSplitted = [TemperatureData[i:i+SizeOfSplit] for i in range(0, len(TemperatureData), SizeOfSplit)]

        if len(TransformerLoading) % len(ListofTimeStamps) != 0:
            TransformerLoadingSplitted, TemperatureDataSplitted = self.ProcessUnevenSequence(TransformerLoadingSplitted), self.ProcessUnevenSequence(TemperatureDataSplitted)

        LossOfLife = ComputeMetricWrapper(TransformerLossofLife,TransformerLoading,TemperatureData,TransformerLifeParameters)

        LossOfLifeArray = []
        for index in range(len(TransformerLoadingSplitted)):
            LossOfLifeArray.append(ComputeMetricWrapper(TransformerLossofLife,TransformerLoadingSplitted[index],TemperatureDataSplitted[index],TransformerLifeParameters))

        return LossOfLife,LossOfLifeArray

    def ProcessUnevenSequence(self,UnevenSequence):

        TempSequence = UnevenSequence
        TempSequence[-1] = TempSequence[-2] + TempSequence[-1]
        TempSequence.remove(TempSequence[-2])
        return TempSequence

    def ProcessForEfficiency(self,ListOfLists,ListofTimeStamps, Indexes):

        # Coputing scalar and time series efficiency

        LossSequence,PowerSequence = [val[Indexes[0]] for val in ListOfLists],[val[Indexes[1]] for val in ListOfLists]

        SizeOfSplit = int(len(LossSequence) / len(ListofTimeStamps))

        LossSequencearr = [sum(arrayslice) for arrayslice in [LossSequence[i:i+SizeOfSplit] for i  in range(0, len(LossSequence), SizeOfSplit)]]
        PowerSequencearr =  [sum(arrayslice) for arrayslice in [PowerSequence[i:i+SizeOfSplit] for i  in range(0, len(PowerSequence), SizeOfSplit)]]

        if len(LossSequence) % len(ListofTimeStamps) !=0:
            LossSequencearr, PowerSequencearr = self.ProcessUnevenSequence(LossSequencearr), self.ProcessUnevenSequence(PowerSequencearr)


        return self.ComputeEfficiency(sum(LossSequence),sum(PowerSequence)), [self.ComputeEfficiency(LossSequencearr[i],PowerSequencearr[i]) for i in range(len(LossSequencearr))]

    def ComputeEfficiency(self,loss,sendingpower):
        if sendingpower <0.001:
            return 100
        else:
            return 100-loss/(10*sendingpower)


    def ProcessListOfDictforEfficiecny(self,ListOfDict,ListofTimeStamps,Indexes):

        # Process List of Dict for scalar and Time series frequency

        ListOfKeys = ['TimeStamp'] + [keys for keys in ListOfDict[0].keys()]

        TemporaryDict, TemporaryDictList  = {keys: [] for keys in ListOfDict[0].keys()}, {keys: [] for keys in ListOfKeys}

        TemporaryDictList['TimeStamp'] = ListofTimeStamps

        for keys in TemporaryDict.keys():
            TemporaryDict[keys], TemporaryDictList[keys] = self.ProcessForEfficiency([Dictionary[keys] for Dictionary in ListOfDict],ListofTimeStamps,Indexes)

        return  TemporaryDict, TemporaryDictList

    def ProcessSequence(self, Sequence, ListofTimeStamps):

        # Process sequence for scalar and time series values
        SizeOfSplit = int(len(Sequence) / len(ListofTimeStamps))
        SequenceSliced = [Sequence[i:i+SizeOfSplit] for i  in range(0, len(Sequence), SizeOfSplit)]

        if len(Sequence) % len(ListofTimeStamps) != 0:
            SequenceSliced = self.ProcessUnevenSequence(SequenceSliced)

        return sum(Sequence), [sum(arrayslice) for arrayslice in SequenceSliced]

    def ProcessListofDict(self,ListOfDict,ListOfTimeStamps):

        # Process for List of Dict for violation risk metrics

        ListOfKeys = ['TimeStamp'] + [keys for keys in ListOfDict[0].keys()]

        TemporaryDict, TemporaryDictList = {keys:[] for keys in ListOfDict[0].keys()},{keys:[] for keys in ListOfKeys}

        TemporaryDictList ['TimeStamp'] = ListOfTimeStamps

        for keys in TemporaryDict.keys():
            TemporaryDict[keys], TemporaryDictList[keys] = self.ProcessSequence([Dictionary[keys] for Dictionary in ListOfDict],ListOfTimeStamps)

        return TemporaryDict, TemporaryDictList