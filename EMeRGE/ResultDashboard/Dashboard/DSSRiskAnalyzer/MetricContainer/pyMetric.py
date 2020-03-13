
'''
All Metric computing class must inherit 'DistributionSystemMetric' class and implement the ComputeMetric function appropriately

List of metric class implemented currently:

VoltageViolationRiskMetric - Input: voltagearray, numofdownwardcustomers, Totalcustomers, simulationtimestep, VupperPU=1.1, VlowerPU=0.9, Output: gamma, VRI
LineOrTransformerViolationRiskMetric - Input: currentarray, limit ,numofdownwardcustomers, Totalcustomers, simulationtimestep, MaxLoadingPU=1.0, Output: alpha, loading, VRI
LineOrTransformerEfficiency - Input: Powerarray, lossarray Output: Peff, Qeff, Ploss, Qloss, Psendpower, Qsendpower
TransformerLossofLife - Input: Loadingarray, temperaturearray, lifeparameterdict, Output: lossoflife
'''


def ComputeMetricWrapper(MetricClass, *argv, **kwargs):
    return MetricClass.ComputeMetric(*argv, **kwargs)

class DistributionSystemMetric:

    def ComputeMetric(*argv, **kwargs):
        return

class VoltageViolationRiskMetric(DistributionSystemMetric):

    def ComputeMetric(*argv, **kwargs):
        # Unpacking argv
        [MagnitudeList, NumOfDownwardCustomers, NumOfTotalCustomers, SimulationTimeStep] = argv

        # Unpacking kwargs
        UpperVoltageLimit, LowerVoltageLimit = kwargs['VupperPU'], kwargs['VlowerPU']

        [maxVoltage, minVoltage] = [max(MagnitudeList), min(MagnitudeList)] if type(MagnitudeList) == list else [MagnitudeList,MagnitudeList]

        if maxVoltage < UpperVoltageLimit and minVoltage > LowerVoltageLimit: gamma = 0
        if maxVoltage > UpperVoltageLimit and minVoltage < LowerVoltageLimit: gamma = max([maxVoltage-UpperVoltageLimit,LowerVoltageLimit-minVoltage])
        if maxVoltage > UpperVoltageLimit and minVoltage > LowerVoltageLimit: gamma = maxVoltage - UpperVoltageLimit
        if maxVoltage < UpperVoltageLimit and minVoltage < LowerVoltageLimit: gamma = LowerVoltageLimit - minVoltage

        return gamma, (NumOfDownwardCustomers/NumOfTotalCustomers)*gamma*SimulationTimeStep

class LineOrTransformerViolationRiskMetric(DistributionSystemMetric):

    def ComputeMetric(*argv, **kwargs):
        import math
        import numpy as np

        if len(argv) == 4: [LoadingPU, NumOfDownwardCustomers, NumOfTotalCustomers, SimulationTimeStep] = argv
        if len(argv) == 5:
            [CurrentRawList, CurrentLimit, NumOfDownwardCustomers, NumOfTotalCustomers, SimulationTimeStep] = argv
            MagnitudeList = [math.sqrt(i ** 2 + j ** 2) for i, j in zip(CurrentRawList[::2], CurrentRawList[1::2])]
            LoadingPU = max(MagnitudeList)/float(CurrentLimit) if kwargs["Tag"] == "Line" else max(MagnitudeList[:int(0.5*len(MagnitudeList))])/float(CurrentLimit)

        alpha = LoadingPU- kwargs['MaxLoadingPU'] if LoadingPU>kwargs['MaxLoadingPU'] else 0
        return alpha,LoadingPU, (NumOfDownwardCustomers/NumOfTotalCustomers)*alpha*SimulationTimeStep

class LineOrTransformerEfficiency(DistributionSystemMetric):

    def ComputeMetric(*argv, **kwargs):
        import math
        import numpy as np

        [ElementPower, ElementLoss] = argv

        # Compute power at from and to buses of an element
        Bus1ElementPower, Bus2ElementPower = ElementPower[:int(0.5 * len(ElementPower))], ElementPower[int(0.5 * len(ElementPower)):]

        # Find out active and reactive power loss
        ActivePowerLoss, ReactivePowerLoss = ElementLoss[0], ElementLoss[1]

        # Find out sending active and reactive power
        SendingActivePower = abs(sum(Bus1ElementPower[::2])) if abs(sum(Bus1ElementPower[::2])) > abs(sum(Bus2ElementPower[::2])) else abs(sum(Bus2ElementPower[::2]))
        SendingReactivePower = abs(sum(Bus1ElementPower[1::2])) if abs(sum(Bus1ElementPower[1::2])) > abs(sum(Bus2ElementPower[1::2])) else abs(sum(Bus2ElementPower[1::2]))

        # Find out efficiency
        ActivePowerEfficiency, ReactivePowerEfficiency = (ActivePowerLoss/(10*SendingActivePower)), (ReactivePowerLoss/(10*SendingReactivePower))

        # Compute for overgeneration (works for transformer only don't use for line)
        Overgeneration = sum(Bus2ElementPower[::2]) - sum(Bus1ElementPower[::2]) if (sum(Bus2ElementPower[::2]) - sum(Bus1ElementPower[::2]))>0 else 0


        return ActivePowerEfficiency,ReactivePowerEfficiency,ActivePowerLoss,ReactivePowerLoss,SendingActivePower,SendingReactivePower, Overgeneration


class TransformerLossofLife(DistributionSystemMetric):

    def ComputeMetric(*argv, **kwargs):
        import math

        # Extract data
        [TransformerLoadingList, TemperatureData, TransformerLifeParametersDict] = argv

        # Initial stff
        TransformerLoadingList,  TemperatureData = TransformerLoadingList+[TransformerLoadingList[0]],  TemperatureData+[TemperatureData[0]]

        theta_ii = TransformerLifeParametersDict['theta_i']
        # Outer iteration loop to make sure convergence
        for ite in range(int(TransformerLifeParametersDict['num_of_iteration'])):
            # Storing Hot spot temperature of Transformer
            TransformerHotSpotTemperatureList = []

            # Loop through all loading values
            for k in range(len(TransformerLoadingList)):
                theta_u = TransformerLifeParametersDict['theta_fl'] * pow((TransformerLoadingList[k] * TransformerLoadingList[k] * TransformerLifeParametersDict['R'] + 1) / (TransformerLifeParametersDict['R'] + 1), TransformerLifeParametersDict['n'])
                theta_not = (theta_u - theta_ii) * (1 - math.exp(-0.25 / TransformerLifeParametersDict['tau'])) + theta_ii
                theta_ii = theta_not
                theta_g = TransformerLifeParametersDict['theta_gfl'] * pow(TransformerLoadingList[k],2 * TransformerLifeParametersDict['m'])
                theta_hst = theta_not + TemperatureData[k] + theta_g
                TransformerHotSpotTemperatureList.append(theta_hst)
            theta_ii = theta_hst - TemperatureData[k] - theta_g

        # Compute Loss of Life of transformer using Hot Spot temperature array
        loss_of_life = sum([100 * 0.25 / pow(10,TransformerLifeParametersDict['A'] + TransformerLifeParametersDict['B'] / (el + 273)) for el in TransformerHotSpotTemperatureList])

        return loss_of_life










