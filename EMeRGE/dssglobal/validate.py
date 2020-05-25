# import standard modules

def validate(config_dict, validation_dict):

    for key, values in config_dict.items():
        
        if isinstance(values,dict):
            for inner_key, inner_values in values.items():
                assert (inner_key in validation_dict[key]), f"'{inner_key}' is not a valid argument."
                assert (isinstance(inner_values,validation_dict[key][inner_key]['type'])), \
                    f"'{inner_key}' can only be of type {validation_dict[key][inner_key]['type']}"
                checkvalues(inner_key,inner_values,validation_dict[key][inner_key])
                    
        else:
            assert (key in validation_dict), f"'{key}' is not a valid argument."
            assert (isinstance(values,validation_dict[key]['type'])), \
                f"'{key}' can only be of type {validation_dict[key]['type']}"
            
            checkvalues(key,values,validation_dict[key])
            

def checkvalues(key,values,dict_tocheck):

    if 'options' in dict_tocheck:
            if values not in dict_tocheck['options']:
                raise ValueError(f" Possible values of {key} are {dict_tocheck['options']} ")

    if 'range' in dict_tocheck:
        if  not dict_tocheck['range'][0] <= values <= dict_tocheck['range'][1]:
            raise ValueError(f" Possible values of {key} are in the range \
                        {dict_tocheck['range']} ")


