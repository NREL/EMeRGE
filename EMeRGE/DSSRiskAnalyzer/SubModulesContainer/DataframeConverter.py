'''
 List of sub-modules for processing dataframe:

 Avialable functionality
 1) Dataframe2DictionaryTwoColumn: e.g. DataFrameConverterWrapper(Dataframe2DictionaryTwoColumn,Dataframe, KeyCol="Keycolumname", ValCol="ValueColname")
 Explanation: Output will be dictionary with keys from values in 'Keycolumnname' and values from values in 'ValueColname'

 '''


def DataFrameConverterWrapper(DataFrameConverterClass, dataframe, **kwargs):
    return DataFrameConverterClass.ConvertDataFrame(dataframe,**kwargs)


class DataframeConverter:

    def ConvertDataframe(dataframe, **kwargs):
        return


class Dataframe2DictionaryTwoColumn(DataframeConverter):

    def ConvertDataframe(dataframe, **kwargs):
        return dict(zip(list(dataframe[kwargs['KeyCol']]),list(dataframe[kwargs['Valcol']])))

