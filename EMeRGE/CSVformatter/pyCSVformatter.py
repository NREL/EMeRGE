import os,pathlib
import toml
import pandas as pd
import shutil
import numpy as np

def readtoml(setting_toml_file):

    texts = ''
    f = open(setting_toml_file, "r")
    text = texts.join(f.readlines())
    settings_dict = toml.loads(text,_dict=dict)
    return settings_dict

def ModifyName(Name):
    InvalidChars = [' ', ',', '.']
    for InvChar in InvalidChars:
        if InvChar in Name:
            Name = Name.replace(InvChar,'-')
    Name = Name.lower()
    return Name 

def export_linecsvs(settings_dict,line_or_cable,ht_or_lt,unique_geometry):
    name = '{}_{}'.format(ht_or_lt,line_or_cable)
    node_dataframe = pd.read_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'CSVfromQGIS',settings_dict[name]['node_file_name']))
    attribute_dataframe = pd.read_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'CSVfromQGIS',settings_dict[name]['attribute_file_name']))
    if 'wiredata.csv' in os.listdir(os.path.join(os.path.join(settings_dict['GIScsvsfolderpath'],'ExtraCSVs'))):
        wiredata = pd.read_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'ExtraCSVs','wiredata.csv'))
        cond_with_geom = list(wiredata.ID)

    node_df = {
        'shapeid' : list(node_dataframe.shapeid),
        'x' : list(node_dataframe.x),
        'y' : list(node_dataframe.y)
    }
    nodecsvname = '{}_{}_nodes.csv'.format(ht_or_lt,line_or_cable)
    node_df = pd.DataFrame.from_dict(node_df)
    node_df.to_csv(os.path.join(settings_dict['GIScsvsfolderpath'],settings_dict['feeder_name'],nodecsvname),index=False)
    print('Exported "{}" file successfully'.format(nodecsvname))

    attributecsvname = '{}_{}_attributes.csv'.format(ht_or_lt,line_or_cable)
    attribute_df = {'shapeid': [],'length':[],'phase':[],'csize':[],'num_of_cond':[],'cname':[],'spacing':[],'units':[]}
    columns = list(attribute_dataframe.columns)
    attribute_df['shapeid'] = list(attribute_dataframe.shapeid)
    for keys,items in settings_dict['line_column_mapper'].items():
        if keys in attribute_df:
            if items[0] == 'force': 
                attribute_df[keys] = [items[1]]*len(attribute_dataframe)
            else:
                if list(set(items)&set(columns)) != []:
                    attribute_df[keys] = list(attribute_dataframe[list(set(items)&set(columns))[0]])
    
    if list(set(settings_dict["line_column_mapper"]["phase_system"])&set(columns)) != []:
        psys = list(attribute_dataframe[list(set(settings_dict["line_column_mapper"]["phase_system"])&set(columns))[0]])
        for el in psys:
            flag = 0
            if el in settings_dict["line_column_mapper"]["four_conductor_system"]:
                attribute_df['num_of_cond'].append(4)
                flag = 1
            if el in settings_dict["line_column_mapper"]["three_conductor_system"]:
                attribute_df['num_of_cond'].append(3)
                flag = 1
            if el in settings_dict["line_column_mapper"]["two_conductor_system"]:
                attribute_df['num_of_cond'].append(2)
                flag =1
            if flag == 0:
                attribute_df['num_of_cond'].append('NA')
    if settings_dict['force_lt_be_three_phase'] == 'yes' and ht_or_lt == 'lt': attribute_df['num_of_cond'] = [4]*len(attribute_dataframe)
    if list(set(settings_dict['line_column_mapper']['nname'])&set(columns)) != []: 
        attribute_df['nname'] = list(attribute_dataframe[list(set(settings_dict['line_column_mapper']['nname'])&set(columns))[0]])
    if list(set(settings_dict['line_column_mapper']['nsize'])&set(columns)) != []: 
        attribute_df['nsize'] = list(attribute_dataframe[list(set(settings_dict['line_column_mapper']['nsize'])&set(columns))[0]])       
    
    for id,val in enumerate(attribute_df['cname']):
        cond = attribute_df['cname'][id]+'_'+ str(attribute_df['csize'][id])
        if cond in cond_with_geom:
            geomid= cond + '_' + str(attribute_df['num_of_cond'][id])+'_'+ attribute_df['spacing'][id]
            if 'nname' in attribute_df:
                geomid = geomid + '_'+ attribute_df['nname'][id]+'_'+ str(attribute_df['nsize'][id])
            if geomid not in list(unique_geometry['ID']):
                unique_geometry['ID'].append(geomid)
                spacing = settings_dict['ht_spacing'] if ht_or_lt == 'ht' else settings_dict['lt_spacing']
                unique_geometry['conductor_spacing'].append(spacing)
                num_of_phases = 3 if attribute_df['phase'][id] == settings_dict['three_phase'] else 1
                unique_geometry['num_of_phases'].append(num_of_phases)
                unique_geometry['num_of_cond'].append(attribute_df['num_of_cond'][id])
                height = settings_dict['height_of_top_conductor_ht'] if ht_or_lt=='ht' else settings_dict['height_of_top_conductor_lt']
                unique_geometry['height_of_top_conductor'].append(height)
                unique_geometry['phase_conductor'].append(cond)
                if 'nname' not in attribute_df and attribute_df['num_of_cond'][id]>num_of_phases:
                    unique_geometry['neutral_conductor'].append(cond)
                if 'nname' not in attribute_df and attribute_df['num_of_cond'][id]==num_of_phases:
                    unique_geometry['neutral_conductor'].append('NA')
                if 'nname' in attribute_df:
                    unique_geometry['neutral_conductor'].append(attribute_df['nname'][id]+'_'+attribute_df['nsize'][id])
                unique_geometry['units'].append(settings_dict['geomtry_units'])
                unique_geometry['spacing'].append(attribute_df['spacing'][id])
            
    attribute_df = pd.DataFrame.from_dict(attribute_df)
    attribute_df.to_csv(os.path.join(settings_dict['GIScsvsfolderpath'],settings_dict['feeder_name'],attributecsvname),index=False)
    print('Exported "{}" file successfully'.format(attributecsvname))

def export_transformercsvs(settings_dict,type):
    csvname = 'distribution_transformer.csv' if type == 'DTs' else 'power_transformer.csv'
    name = 'distribution_transformer' if type == 'DTs' else 'power_transformer'
    attribute_df = {'ID': [],'KVA_cap':[],'HV_KV':[],'LV_KV':[],'maxtap':[],'mintap':[],'tap':[],'numtaps':[],'prim_con':[],'sec_con':[],'vector_group':[],'x':[],'y':[],'%resistance':[],'%reactance':[],'%noloadloss':[],'phase':[] }
    attribute_dataframe = pd.read_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'CSVfromQGIS',settings_dict[name]['file_name']))
    columns = list(attribute_dataframe.columns)
    for keys,items in settings_dict['transformer_column_mapper'].items():
        if keys in attribute_df:
            if items[0] == 'force': 
                attribute_df[keys] = [items[1]]*len(attribute_dataframe)
            else:
                if list(set(items)&set(columns)) != []:
                    attribute_df[keys] = list(attribute_dataframe[list(set(items)&set(columns))[0]])
    if settings_dict["MVA_to_KVA_conversion_for_PT"] == "yes" and type != 'DTs': attribute_df['KVA_cap'] = [el*1000 for el in attribute_df['KVA_cap']]
    if type == 'PTs':
        col,val = [],[]
        for keys,items in attribute_df.items():
            val.append(items[settings_dict['PTrow']])
            col.append(keys)
        attribute_df = pd.DataFrame.from_dict({'0':val},orient='index',columns=col)
    else:
        attribute_df = pd.DataFrame.from_dict(attribute_df)
    attribute_df.to_csv(os.path.join(settings_dict['GIScsvsfolderpath'],settings_dict['feeder_name'],csvname),index=False)
    print('Exported "{}" file successfully'.format(csvname))


def extend_data(dataframe,settings_dict,tdata,load):
        cols = list(dataframe.columns)
        t_col = list(set(settings_dict['consumer_column_mapper']['tariff_type'])&set(cols))[0]
        tdata.extend(list(dataframe[t_col]))
        l_col = list(set(settings_dict['consumer_column_mapper']['Sanctioned_load'])&set(cols))[0] 
        load.extend(list(dataframe[l_col]))
        return tdata,load

def export_consumercsvs(settings_dict,type):
    name = '{}_consumer'.format(type)
    csvname = 'consumer_{}.csv'.format(type)
    attribute_df = {'ID':[],'pf':[],'phase':[],'x':[],'y':[],'kv':[],'load_type':[],'kw':[],'tec':[],'cust_type':[]}
    attribute_dataframe = pd.read_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'CSVfromQGIS',settings_dict[name]['file_name']))
    columns = list(attribute_dataframe.columns)
    for keys,items in settings_dict['consumer_column_mapper'].items():
        if keys in attribute_df:
            if items[0] == 'force': 
                attribute_df[keys] = [items[1]]*len(attribute_dataframe)
            else:
                if list(set(items)&set(columns)) != []:
                    attribute_df[keys] = list(attribute_dataframe[list(set(items)&set(columns))[0]])
    #print("As a final check make sure that voltage level is same for all single phase customers in {} file and same is true for all three phase customers otherwise you may encounter problem while running generated DSS files".format(csvname))
    for el in attribute_df['phase']:
        if el in settings_dict['single_phase'] and type=='lt':
            attribute_df['kv'].append(settings_dict['Consumer_kv']['lt_consumer_phase'])
        if el == settings_dict['three_phase'] and type=='lt':
            attribute_df['kv'].append(settings_dict['Consumer_kv']['lt_consumer_ll'])
        if el in settings_dict['single_phase'] and type=='ht':
            attribute_df['kv'].append(settings_dict['Consumer_kv']['ht_consumer_phase'])
        if el == settings_dict['three_phase'] and type=='ht':
            attribute_df['kv'].append(settings_dict['Consumer_kv']['ht_consumer_ll'])
        
    
    index = range(len(attribute_dataframe))
    attribute_df['ID'] = [ModifyName(settings_dict['feeder_name'])+type+str(id) for id in index]
    
    # figuring out type of customers depending on tariff class
    tariff_col = list(set(settings_dict['consumer_column_mapper']['tariff_type'])&set(columns))[0]
    tariff_data = list(attribute_dataframe[tariff_col])
    for el in tariff_data:
        for keys, items in settings_dict['consumer_class_by_tariff'].items():
            if el in items: attribute_df['cust_type'].append(keys.lower())
    attribute_df['load_type'] = [settings_dict['load_type']['lt_consumer']]*len(attribute_dataframe) if type == 'lt' else [settings_dict['load_type']['ht_consumer']]*len(attribute_dataframe)

    if settings_dict['consumer_column_mapper']['estimate_consumer_peakkw'] == 'yes':
        tdata,load = [], []
        if settings_dict['lt_consumer']['file_name'] in list_of_csvs: 
            dataframe = pd.read_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'CSVfromQGIS',settings_dict['lt_consumer']['file_name']))
            tdata,load = extend_data(dataframe,settings_dict,tdata,load)
            
        if settings_dict['ht_consumer']['file_name'] in list_of_csvs:
            dataframe = pd.read_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'CSVfromQGIS',settings_dict['ht_consumer']['file_name']))
            tdata,load = extend_data(dataframe,settings_dict,tdata,load)
        
        consumerdata = []
        for el in tdata:
            for keys, items in settings_dict['consumer_class_by_tariff'].items():
                if el in items: consumerdata.append(keys.lower())
        unique_consumer_type = np.unique(consumerdata)
        sum_dict ={}
        for uta in unique_consumer_type:
            ids = [i for i, value in enumerate(consumerdata) if value == uta]
            sum_dict[uta] = sum([load[el] for el in ids])
        
        sanctioned_column = list(set(settings_dict['consumer_column_mapper']['Sanctioned_load'])&set(columns))[0]
        sanctioned_load = list(attribute_dataframe[sanctioned_column])
        index = 0
        for l in sanctioned_load:
            kw = l*settings_dict['consumer_column_mapper']['PeakMWload']*1000*settings_dict['peak_contribution'][attribute_df['cust_type'][index]]/sum_dict[attribute_df['cust_type'][index]]
            attribute_df['kw'].append(kw)
            attribute_df['tec'].append(kw*settings_dict['tec_per_kw_by_consumer_type'][attribute_df['cust_type'][index]])
            index +=1
    attribute_df = pd.DataFrame.from_dict(attribute_df)
    attribute_df.to_csv(os.path.join(settings_dict['GIScsvsfolderpath'],settings_dict['feeder_name'],csvname),index=False)
    print('Exported "{}" file successfully'.format(csvname))


def ClearProjectFolder(path):
    print('Creating / cleaning folder: ',  path)
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    for root, dirs, files in os.walk(path):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    return


def append_geometry(unique_geometry,tag):
    id = settings_dict[tag]['phase_conductor']+'_'+str(settings_dict[tag]['num_of_cond'])+ '_'+ settings_dict[tag]['spacing']
    if id not in list(unique_geometry["ID"]):
        unique_geometry["ID"].append(id)
        for keys, items in settings_dict[tag].items():
            unique_geometry[keys].append(items)
    return unique_geometry

class CSVFormatter:

    def __init__(self, setting_toml_file):

        settings_dict = readtoml(setting_toml_file)

        list_of_csvs = os.listdir(os.path.join(settings_dict['GIScsvsfolderpath'],'CSVfromQGIS'))

        ClearProjectFolder(os.path.join(settings_dict['GIScsvsfolderpath'],settings_dict['feeder_name']))
        unique_geometry = {'ID':[],'conductor_spacing':[],'num_of_cond':[],'num_of_phases':[],'height_of_top_conductor':[],'phase_conductor':[],'neutral_conductor':[],'units':[],'spacing':[]}

        if settings_dict['ht_line']['node_file_name'] in list_of_csvs and settings_dict['ht_line']['node_file_name'] in list_of_csvs:
            export_linecsvs(settings_dict,'line','ht',unique_geometry)
        if settings_dict['ht_cable']['node_file_name'] in list_of_csvs and settings_dict['ht_cable']['node_file_name'] in list_of_csvs:
            export_linecsvs(settings_dict,'cable','ht',unique_geometry)
        if settings_dict['lt_line']['node_file_name'] in list_of_csvs and settings_dict['lt_line']['node_file_name'] in list_of_csvs:
            export_linecsvs(settings_dict,'line','lt',unique_geometry)
        if settings_dict['lt_cable']['node_file_name'] in list_of_csvs and settings_dict['lt_cable']['node_file_name'] in list_of_csvs:
            export_linecsvs(settings_dict,'cable','lt',unique_geometry)
    
        if "Service_wire_single_phase" in settings_dict:
            unique_geometry = append_geometry(unique_geometry,'Service_wire_single_phase')
        if "Service_wire_three_phase" in settings_dict:
            unique_geometry = append_geometry(unique_geometry,'Service_wire_three_phase')
        if "ht_three_phase" in settings_dict:
            unique_geometry = append_geometry(unique_geometry,'ht_three_phase')
    
        csvname = 'linegeometry.csv'
        unique_geometry = pd.DataFrame.from_dict(unique_geometry)
        unique_geometry.to_csv(os.path.join(settings_dict['GIScsvsfolderpath'],'ExtraCSVs',csvname),index=False)
        print('Exported "{}" file successfully'.format(csvname))


        if settings_dict['distribution_transformer']['file_name'] in list_of_csvs:
            export_transformercsvs(settings_dict,'DTs')
        if settings_dict['power_transformer']['file_name'] in list_of_csvs:
            export_transformercsvs(settings_dict,'PTs')
        if settings_dict['lt_consumer']['file_name'] in list_of_csvs:
            export_consumercsvs(settings_dict,'lt')
        if settings_dict['ht_consumer']['file_name'] in list_of_csvs:
            export_consumercsvs(settings_dict,'ht')


if __name__ == '__main__':
    
    setting_toml_file = r'C:\Users\KDUWADI\Desktop\NREL_Projects\CIFF-TANGEDCO\TANGEDCO\SoftwareTools\GIS_CSVs_to_Standard_CSVs\csvsetting.toml'
    CSVFormatter(setting_toml_file)