import pandas as pd
import calendar
import os

class Template:

    """ A class which generates template for combining monthly results including .toml file
    
    :param FolderPath: A folder path where you want to create project
    :type FolderPath: str
    """

    def __init__(self, FolderPath):
        
        # Create Folders
        FolderName = "Monthy2YearlyFolderTemplate"
        os.mkdir(os.path.join(FolderPath,FolderName))
        os.mkdir(os.path.join(FolderPath,FolderName,"MonthlyResults"))
        print("{} created successfully".format(os.path.join(FolderPath,FolderName,"MonthlyResults")))

        os.mkdir(os.path.join(FolderPath,FolderName,"YearlyResults"))
        print("{} created successfully".format(os.path.join(FolderPath,FolderName,"MonthlyResults")))


class Monthly2Yearly:

    """ A class for combining monthly results.
    
    :param inputpath: A path where all monthly results are stored
    :type inputpath: str
    :param outputpath: A path where you want to store results
    :type outputpath: str
    :param DoNotReadFiles: list of files to avoid combining
    :type DoNotReadFiles: list, optional
    :return: csv files
    """

    def __init__(self,inputpath, outputpath, DoNotReadFiles=[]):

        # Put all foldername in order in a list
        FolderNameList = ['Category_'+calendar.month_name[i+1][0:3] for i in range(12)]
        PVScenarios_list = ['{}.0%-customer-100.0%-PV'.format((i+1)*10) for i in range(10)]
        PVScenarios_list = PVScenarios_list+['Base']
        MetricAddition = ['{}Asset.csv'.format(metric) for metric in ['CRI','LVRI','TVRI','NVRI','TLOF','TOG']]
        MetricAverage= ['{}Asset.csv'.format(metric) for metric in ['LE','TE']]


        # Walk through all folders inside input path

        for PVScenario in PVScenarios_list:
            AllDataDict = {}
            print('Converting monthly result to annual for {} scenario ..............................................'.format(PVScenario))
            if not os.path.exists(os.path.join(outputpath,PVScenario)): os.mkdir(os.path.join(outputpath,PVScenario))

            for Folder in FolderNameList:
                assert os.path.exists(os.path.join(inputpath,Folder,PVScenario)),'{} does not exists.'.format(os.path.join(inputpath,Folder,PVScenario))
                for files in os.listdir(os.path.join(inputpath,Folder,PVScenario)):
                    if 'TimeSeries.csv' in files and files not in DoNotReadFiles:
                        if files not in AllDataDict: AllDataDict[files] = []
                        AllDataDict[files].append(pd.read_csv(os.path.join(inputpath,Folder,PVScenario,files)))

                    elif files not in DoNotReadFiles:

                        if files not in AllDataDict:
                            AllDataDict[files] = pd.read_csv(os.path.join(inputpath,Folder,PVScenario,files))
                        else:
                            this_dataframe = pd.read_csv(os.path.join(inputpath,Folder,PVScenario,files))
                            AllDataDict[files]['Values']  =[sum(x) for x in zip(AllDataDict[files]['Values'].tolist(),this_dataframe['Values'].tolist())]


            for keys, values in AllDataDict.items():
                if 'TimeSeries.csv' in keys:
                    df = pd.concat(values)
                    df.to_csv(os.path.join(outputpath,PVScenario,keys),index=False)
                    print('{} created successfully'.format(os.path.join(outputpath,PVScenario,keys)))

                elif keys in MetricAverage:
                    values['Values'] = [el/12 for el in values['Values']]
                    values.to_csv(os.path.join(outputpath, PVScenario, keys), index=False)
                    print('{} created successfully'.format(os.path.join(outputpath, PVScenario, keys)))

                elif keys == 'SystemLevelMetrics.csv':
                    datadict = dict(zip(values['Metrics'],values['Values']))
                    keys_to_average = ['SE_line','SE_transformer','SE']
                    for key,val in datadict.items():
                        if key in keys_to_average: datadict[key] = val/12
                    datadictmodified = {'Metrics':[k for k in datadict.keys()],'Values': [v for k,v in datadict.items()]}
                    df = pd.DataFrame.from_dict(datadictmodified)
                    df.to_csv(os.path.join(outputpath, PVScenario, keys), index=False)
                    print('{} created successfully'.format(os.path.join(outputpath, PVScenario, keys)))
                else:
                    values.to_csv(os.path.join(outputpath,PVScenario,keys),index=False)
                    print('{} created successfully'.format(os.path.join(outputpath, PVScenario, keys)))


if __name__ =='__main__':

    inputpath = r"C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\CombineMonthlyResults\MonthlyResults\GWC"
    outputpath = r"C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\CombineMonthlyResults\YearlyResults\GWC"
    DonotReadFilesList = ['voltagemagAssetTimeSeries.csv','lineloadingAssetTimeSeries.csv','transformerloadingAssetTimeSeries.csv']
    
    Monthly2Yearly(inputpath,outputpath,DonotReadFilesList)




