import numpy as np
from DSSRiskAnalyzer.MetricContainer.pyMetric import *


# A wrapper function to call desired
def DistributionSystemMetricWrapper(ElementClass, **kwargs):
    return ElementClass(**kwargs).ComputeDistributionSystemMetrics(**kwargs)


class MetricsAbstract:

    ''' Abstract class for Metrics'''
    def __init__(self,**kwargs):

        self.DSS = kwargs['DSSobject']
        self.Circuit = self.DSS.Circuit
        self.Bus = self.DSS.Bus
        self.Loads = self.DSS.Loads
        self.Element = self.DSS.CktElement
        self.DSSClass = self.DSS.ActiveClass
        self.SimulationSettings = kwargs['SimulationSettings']
        self.TotalCustomers = self.Loads.Count()
        self.OutputDict = {'VRI': {},
                           'CRI_weight': {LoadName: 0 for LoadName in self.Loads.AllNames()},
                           'SARDI': [],
                           'ImpactedCustomersList': []}

    def ComputeDistributionSystemMetrics(self, **kwargs):
        return

class SystemMetric(MetricsAbstract):


    def ComputeDistributionSystemMetrics(self,**kwargs):
        import numpy as np
        # Extract
        NodeDict, LineDict, TransformerDict = kwargs['Node'], kwargs['Line'],kwargs['Transformer']

        # Impacted customers
        self.OutputDict['ImpactedCustomersList'] = NodeDict['ImpactedCustomersList']+LineDict['ImpactedCustomersList']+TransformerDict['ImpactedCustomersList']

        # Update VRI
        self.OutputDict['SARDI'] = len(np.unique(self.OutputDict['ImpactedCustomersList'])) * self.SimulationSettings['simulation_time_step'] / self.TotalCustomers

        # Update CRI_weight for all customers
        for LoadName, Values in self.OutputDict['CRI_weight'].items():
            self.OutputDict['CRI_weight'][LoadName] = (NodeDict['CRI_weight'][LoadName] + LineDict['CRI_weight'][LoadName] + TransformerDict['CRI_weight'][LoadName])/self.SimulationSettings['simulation_time_step']


        # Computing total loss and power for all lines
        LineLossPowerArray = [effarray[2:6] for Line, effarray in LineDict['EfficiencyMetric'].items()]
        LineLossPowerArrayzipped = list(zip(*LineLossPowerArray))
        #self.OutputDict['LineLossPower'] = [sum(array) for array in list(zip(*LineLossPowerArray))]
        self.OutputDict['LineLossPower'] = [sum(LineLossPowerArrayzipped[0]),sum(LineLossPowerArrayzipped[1]),max(LineLossPowerArrayzipped[2]),max(LineLossPowerArrayzipped[3])]

        # Computing total loss and power for all transformers
        TransformerLossPowerArray = [effarray[2:6] for Transformer, effarray in TransformerDict['EfficiencyMetric'].items()]
        TransformerLossPowerArrayzipped = list(zip(*TransformerLossPowerArray))
        #self.OutputDict['TransformerLossPower'] = [sum(array) for array in list(zip(*TransformerLossPowerArray))]
        self.OutputDict['TransformerLossPower'] = [sum(TransformerLossPowerArrayzipped[0]),sum(TransformerLossPowerArrayzipped[1]),max(TransformerLossPowerArrayzipped[2]),max(TransformerLossPowerArrayzipped[3])]

        # Computing total loss and power for both line and transformers
        Totallosspowerzipped = list(zip(*[self.OutputDict['LineLossPower'],self.OutputDict['TransformerLossPower']]))
        #self.OutputDict['TotalLossPower'] = [sum(array) for array in zip(*[self.OutputDict['LineLossPower'],self.OutputDict['TransformerLossPower']])]
        self.OutputDict['TotalLossPower'] = [sum(Totallosspowerzipped[0]),sum(Totallosspowerzipped[1]),max(Totallosspowerzipped[2]),max(Totallosspowerzipped[3])]

        # Compute overgeneration for whole network
        self.OutputDict['Overgeneration'] = round(self.Circuit.TotalPower()[0]) if self.Circuit.TotalPower()[0]>0 else 0

        return self.OutputDict


class NodalMetric(MetricsAbstract):

    def ComputeDistributionSystemMetrics(self,**kwargs):
        import numpy as np

       # Loop through all buses
        for BusName in self.Circuit.AllBusNames():

            # Activate Bus
            self.Circuit.SetActiveBus(BusName)

            # Extract voltage magnitude only (using even filter) from all phases and NodeName
            VoltageMagnitudeList, NodeName = self.Bus.puVmagAngle()[::2], BusName.split('.')[0].lower()

            # Compute gamma and Voltage Violation Risk Index
            gamma, self.OutputDict['VRI'][NodeName] = ComputeMetricWrapper(VoltageViolationRiskMetric,
                                                                                      VoltageMagnitudeList,len(kwargs['NodeCustDown'][NodeName]),self.TotalCustomers,self.SimulationSettings['simulation_time_step'],
                                                                                      VupperPU=self.SimulationSettings['voltage_upper_limit'],VlowerPU=self.SimulationSettings['voltage_lower_limit'])
            # Populate ImpactedCustomersList for all voltage violations
            if gamma !=0: self.OutputDict['ImpactedCustomersList'].extend(kwargs['NodeCustDown'][NodeName])

            if 'VoltageMag' not in self.OutputDict: self.OutputDict['VoltageMag'] = {}
            self.OutputDict['VoltageMag'][BusName] = max(VoltageMagnitudeList)

            # Update Customers Risk Index(CRI) Weight for all customers if it is less than previous value
            for LoadName in kwargs['NodeCustDown'][NodeName]:
                if self.OutputDict['CRI_weight'][LoadName] < gamma: self.OutputDict['CRI_weight'][LoadName]  = gamma

        # Compute System Average Risk Duration Index
        self.OutputDict['SARDI'] = len(np.unique(self.OutputDict['ImpactedCustomersList'])) * self.SimulationSettings['simulation_time_step'] / self.TotalCustomers

        return self.OutputDict

class LineMetric(MetricsAbstract):

    def ComputeDistributionSystemMetrics(self,**kwargs):


        # Activate line element and loop through all line elements
        self.Circuit.SetActiveClass("Line")
        flag = self.DSSClass.First()

        while flag > 0:

            # Extract linename, linecurrent and linelimit
            LineName, LineCurrentRawList, LineLimit  = self.Element.Name().split('.')[1], self.Element.Currents(), self.Element.NormalAmps()

            # Compute alpha and line violation risk index
            alpha, loadingPU, self.OutputDict['VRI'][LineName] = ComputeMetricWrapper(LineOrTransformerViolationRiskMetric,
                                                                                      LineCurrentRawList, LineLimit, len(kwargs['LineCustDown'][LineName]),self.TotalCustomers,self.SimulationSettings['simulation_time_step'],
                                                                                      MaxLoadingPU=self.SimulationSettings['line_loading_upper_limit'],Tag='Line')

            # Store Impacted customers if there is line violation
            if alpha !=0: self.OutputDict['ImpactedCustomersList'].extend(kwargs['LineCustDown'][LineName])

            # Update Customers Risk Index(CRI) Weight for all customers if it is less than previous value
            for LoadName in kwargs['LineCustDown'][LineName]:
                if self.OutputDict['CRI_weight'][LoadName] < alpha: self.OutputDict['CRI_weight'][LoadName]= alpha

            # Compute Efficiency
            if 'EfficiencyMetric' not in self.OutputDict: self.OutputDict['EfficiencyMetric'] = {}
            self.OutputDict['EfficiencyMetric'][LineName] = ComputeMetricWrapper(LineOrTransformerEfficiency,self.Element.Powers(),self.Element.Losses())

            if 'PULoading' not in self.OutputDict: self.OutputDict['PULoading'] = {}
            self.OutputDict['PULoading'][LineName] = loadingPU

            flag = self.DSSClass.Next()

        # Compute System Average Risk Duration Index
        self.OutputDict['SARDI'] = len(np.unique(self.OutputDict['ImpactedCustomersList'])) * self.SimulationSettings['simulation_time_step'] / self.TotalCustomers

        return self.OutputDict

class TransformerMetric(MetricsAbstract):

    def ComputeDistributionSystemMetrics(self,**kwargs):


        # Activate line element and loop through all line elements
        self.Circuit.SetActiveClass("Transformer")
        flag = self.DSSClass.First()

        while flag > 0:

            # Extract transformername, transformercurrent and transformerlimit
            TransformerName, TransformerCurrentRawList, TransformerLimit  = self.Element.Name().split('.')[1], self.Element.Currents(), self.Element.NormalAmps()

            # Compute beta and transformer violation risk index
            beta, TransformerPUloading, self.OutputDict['VRI'][TransformerName] = ComputeMetricWrapper(LineOrTransformerViolationRiskMetric,
                                                                                      TransformerCurrentRawList, TransformerLimit, len(kwargs['TransformerCustDown'][TransformerName]),self.TotalCustomers,self.SimulationSettings['simulation_time_step'],
                                                                                      MaxLoadingPU=self.SimulationSettings['transformer_loading_upper_limit'],Tag='Transformer')

            # Store Transformer loading
            if 'PULoading' not in self.OutputDict: self.OutputDict['PULoading'] = {}
            self.OutputDict['PULoading'][TransformerName] = TransformerPUloading

            # Store Impacted customers if there is line violation
            if beta !=0: self.OutputDict['ImpactedCustomersList'].extend(kwargs['TransformerCustDown'][TransformerName])

            # Update Customers Risk Index(CRI) Weight for all customers if it is less than previous value
            for LoadName in kwargs['TransformerCustDown'][TransformerName]:
                if self.OutputDict['CRI_weight'][LoadName] < beta: self.OutputDict['CRI_weight'][LoadName]= beta

            # Compute Efficiency
            if 'EfficiencyMetric' not in self.OutputDict: self.OutputDict['EfficiencyMetric'] = {}
            self.OutputDict['EfficiencyMetric'][TransformerName] = ComputeMetricWrapper(LineOrTransformerEfficiency,self.Element.Powers(),self.Element.Losses())

            if 'Overgeneration' not in self.OutputDict: self.OutputDict['Overgeneration']  ={}
            self.OutputDict['Overgeneration'][TransformerName] = round(self.OutputDict['EfficiencyMetric'][TransformerName][-1],3)

            flag = self.DSSClass.Next()

        # Compute System Average Risk Duration Index
        self.OutputDict['SARDI'] = len(np.unique(self.OutputDict['ImpactedCustomersList'])) * self.SimulationSettings['simulation_time_step'] / self.TotalCustomers

        return self.OutputDict











