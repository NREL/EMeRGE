'''
All file reader must inherit 'FileReader' class and implement the readfile function appropriately

List of file readers implemented currently

CSVReader - takes csvfile and kwargs spits out pandas dataframe
TomlReader - takes tomlfile and splits out dictionary
PickleReader - takes pickle file and splits out what had been stored

'''

def ReadFromFile(filepath,**kwargs):
    import os
    file_extension = os.path.splitext(filepath)[-1].lower()
    assert file_extension in Mapping_dict,'{} is not yet implemented to read ....'.format(file_extension)
    return ReaderWrapper(Mapping_dict[file_extension],filepath,**kwargs)

def ReaderWrapper(ReaderClass,filepath,**kwargs):
    return ReaderClass.ReadFile(filepath,**kwargs)


class FileReader:
    # Boiler plate for reading files
    def ReadFile(filepath, **kwargs):
        return

class ReadPickle(FileReader):

    def ReadFile(picklefilepath, **kwargs):
        import pickle
        return pickle.load(open(picklefilepath,"rb"))


class ReadCSV(FileReader):

    def ReadFile(csvfilepath, **kwargs):
        import pandas as pd
        return pd.read_csv(csvfilepath,**kwargs)

class ReadToml(FileReader):

    def ReadFile(tomlfilepath,**kwargs):
        import toml
        texts = ''
        file = open(tomlfilepath, "r")
        contents = texts.join(file.readlines())
        content_dict = toml.loads(contents, _dict=dict)
        return content_dict


Mapping_dict = {
    '.csv' : ReadCSV,
    '.toml': ReadToml,
    '.p' : ReadPickle
}
