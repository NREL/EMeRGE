# Standard imports
import os,pathlib
import shutil
import logging
import json

# Third party imports
import numpy as np
import pandas as pd

# Internal imports
from csvformatter.constants import DEFAULT_CONFIGURATION, VALID_SETTINGS
from dssglobal.validate import validate
from dssglobal.logger import getLogger

class CSVFormatter:
    
    """ A class for formatting CSVs extracted from :class:`gis2.csv` 
    
    :param settings_toml_file: A path to .toml file containg all the settings necessary for conversion
    :type settings_toml_file: str
    :return: csv files
    """

    def __init__(self, config_path=None):

        """ A constructor method for :class:`CSVFormatter` """

        if config_path != None:

            if isinstance(config_path,dict):
                config_dict = config_path
            else:
                if config_path.endswith('.json'):
                    with open(config_path,'r') as json_file:
                        config_dict = json.load(json_file)
            
            self.settings = {**DEFAULT_CONFIGURATION,**config_dict}

            # Validate input
            validate(self.settings,VALID_SETTINGS)

            self.logger = getLogger(self.settings['log_settings'])
            
            list_of_csvs = os.listdir(os.path.join(self.settings['project_path'],
                        'GISCSVs'))

            self.clear_folder(os.path.join(self.settings['project_path'],\
                                self.settings['feeder_name']))
            
            unique_geometry = { 'ID':[],
                                'conductor_spacing':[],
                                'num_of_cond':[],
                                'num_of_phases':[],
                                'height_of_top_conductor':[],
                                'phase_conductor':[],
                                'neutral_conductor':[],
                                'units':[],
                                'spacing':[]
                            }

            if self.settings['ht_line']['node_file_name'] in list_of_csvs and \
                        self.settings['ht_line']['node_file_name'] in list_of_csvs:

                self.export_linecsvs('line','ht',unique_geometry)
            
            if self.settings['ht_cable']['node_file_name'] in list_of_csvs and \
                    self.settings['ht_cable']['node_file_name'] in list_of_csvs:
                
                self.export_linecsvs('cable','ht',unique_geometry)
            
            if self.settings['lt_line']['node_file_name'] in list_of_csvs and \
                    self.settings['lt_line']['node_file_name'] in list_of_csvs:
                
                self.export_linecsvs('line','lt',unique_geometry)
            
            if self.settings['lt_cable']['node_file_name'] in list_of_csvs and \
                    self.settings['lt_cable']['node_file_name'] in list_of_csvs:
                
                self.export_linecsvs('cable','lt',unique_geometry)
        
            if "Service_wire_single_phase" in self.settings:
                unique_geometry = self.append_geometry(unique_geometry, 'Service_wire_single_phase')
            if "Service_wire_three_phase" in self.settings:
                unique_geometry = self.append_geometry(unique_geometry,'Service_wire_three_phase')
            if "ht_three_phase" in self.settings:
                unique_geometry = self.append_geometry(unique_geometry, 'ht_three_phase')
        
            csvname = 'linegeometry.csv'
            unique_geometry = pd.DataFrame.from_dict(unique_geometry)
            unique_geometry.to_csv(os.path.join(self.settings['project_path'],
                    'ExtraCSVs',csvname),index=False)
            self.logger.info('Exported "{}" file successfully'.format(csvname))


            if self.settings['distribution_transformer']['file_name'] in list_of_csvs:
                self.export_transformercsvs('DTs')
            if self.settings['power_transformer']['file_name'] in list_of_csvs:
                self.export_transformercsvs('PTs')

            if self.settings['lt_consumer']['file_name'] in list_of_csvs:
                self.export_consumercsvs(list_of_csvs,'lt')
            if self.settings['ht_consumer']['file_name'] in list_of_csvs:
                self.export_consumercsvs(list_of_csvs,'ht')

    def modify_name(self,name):

        invalid_chars = [' ', ',', '.']
        for inv_char in invalid_chars:
            if inv_char in name:
                name = name.replace(inv_char,'-')
        name = name.lower()
        return name 
    
    
    def extend_data(self,dataframe,tdata,load):

        cols = list(dataframe.columns)
        
        t_col = list(set(self.settings['consumer_column_mapper']['tariff_type'])&set(cols))[0]
        
        tdata.extend(list(dataframe[t_col]))
        
        l_col = list(set(self.settings['consumer_column_mapper']['Sanctioned_load'])&set(cols))[0] 
        
        load.extend(list(dataframe[l_col]))
        
        return tdata,load
    
    def export_consumercsvs(self,list_of_csvs,type):
        
        name = '{}_consumer'.format(type)
        
        csvname = 'consumer_{}.csv'.format(type)
        
        attribute_df = {'ID':[],
                        'pf':[],
                        'phase':[],
                        'x':[],
                        'y':[],
                        'kv':[],
                        'load_type':[],
                        'kw':[],
                        'tec':[],
                        'cust_type':[]
                    }
        
        attribute_dataframe = pd.read_csv(os.path.join(self.settings['project_path'], \
                'GISCSVs',self.settings[name]['file_name']))
        
        columns = list(attribute_dataframe.columns)
        
        for keys,items in self.settings['consumer_column_mapper'].items():
            if keys in attribute_df:
                if items[0] == 'force': 
                    attribute_df[keys] = [items[1]]*len(attribute_dataframe)
                else:
                    if list(set(items)&set(columns)) != []:
                        attribute_df[keys] = list(attribute_dataframe[list(set(items)&set(columns))[0]])
        
        #print("As a final check make sure that voltage level is same for all single phase 
        # customers in {} file and same is true for all three phase customers otherwise you
        #  may encounter problem while running generated DSS files".format(csvname))

        for el in attribute_df['phase']:
            if el in self.settings['single_phase'] and type=='lt':
                attribute_df['kv'].append(self.settings['Consumer_kv']['lt_consumer_phase'])
            if el == self.settings['three_phase'] and type=='lt':
                attribute_df['kv'].append(self.settings['Consumer_kv']['lt_consumer_ll'])
            if el in self.settings['single_phase'] and type=='ht':
                attribute_df['kv'].append(self.settings['Consumer_kv']['ht_consumer_phase'])
            if el == self.settings['three_phase'] and type=='ht':
                attribute_df['kv'].append(self.settings['Consumer_kv']['ht_consumer_ll'])
            
        
        index = range(len(attribute_dataframe))
        attribute_df['ID'] = [self.modify_name(self.settings['feeder_name'])+type+str(id) for id in index]
        
        # figuring out type of customers depending on tariff class
        tariff_col = list(set(self.settings['consumer_column_mapper']['tariff_type'])&set(columns))[0]
        tariff_data = list(attribute_dataframe[tariff_col])
        for el in tariff_data:
            for keys, items in self.settings['consumer_class_by_tariff'].items():
                if el in items: attribute_df['cust_type'].append(keys.lower())
        attribute_df['load_type'] = [self.settings['load_type']['lt_consumer']]*len(attribute_dataframe) \
            if type == 'lt' else [self.settings['load_type']['ht_consumer']]*len(attribute_dataframe)

        if self.settings['consumer_column_mapper']['estimate_consumer_peakkw'] == 'yes':
            tdata,load = [], []
            if self.settings['lt_consumer']['file_name'] in list_of_csvs: 
                dataframe = pd.read_csv(os.path.join(self.settings['project_path'],'GISCSVs',\
                    self.settings['lt_consumer']['file_name']))
                tdata,load = self.extend_data(dataframe,tdata,load)
                
            if self.settings['ht_consumer']['file_name'] in list_of_csvs:
                dataframe = pd.read_csv(os.path.join(self.settings['project_path'],'GISCSVs',\
                    self.settings['ht_consumer']['file_name']))
                tdata,load = self.extend_data(dataframe,tdata,load)
            
            consumerdata = []
            for el in tdata:
                for keys, items in self.settings['consumer_class_by_tariff'].items():
                    if el in items: consumerdata.append(keys.lower())
            unique_consumer_type = np.unique(consumerdata)
            sum_dict ={}
            for uta in unique_consumer_type:
                ids = [i for i, value in enumerate(consumerdata) if value == uta]
                sum_dict[uta] = sum([load[el] for el in ids])
            
            sanctioned_column = list(set(self.settings['consumer_column_mapper']\
                            ['Sanctioned_load'])&set(columns))[0]
            sanctioned_load = list(attribute_dataframe[sanctioned_column])
            index = 0
            for l in sanctioned_load:
                
                kw = l*self.settings['consumer_column_mapper']['PeakMWload']*1000\
                        *self.settings['peak_contribution'][attribute_df['cust_type'][index]]\
                        /sum_dict[attribute_df['cust_type'][index]]
                
                attribute_df['kw'].append(kw)
                
                attribute_df['tec'].append(kw*self.settings['tec_per_kw_by_consumer_type']\
                    [attribute_df['cust_type'][index]])
                index +=1
        attribute_df = pd.DataFrame.from_dict(attribute_df)
        attribute_df.to_csv(os.path.join(self.settings['project_path'],\
            self.settings['feeder_name'],csvname),index=False)
        self.logger.info('Exported "{}" file successfully'.format(csvname))

    
    def export_transformercsvs(self,type):
        
        csvname = 'distribution_transformer.csv' if type == 'DTs' else 'power_transformer.csv'
        
        name = 'distribution_transformer' if type == 'DTs' else 'power_transformer'
        
        attribute_df = {'ID': [],
                        'KVA_cap':[],
                        'HV_KV':[],
                        'LV_KV':[],
                        'maxtap':[],
                        'mintap':[],
                        'tap':[],
                        'numtaps':[],
                        'prim_con':[],
                        'sec_con':[],
                        'vector_group':[],
                        'x':[],
                        'y':[],
                        '%resistance':[],
                        '%reactance':[],
                        '%noloadloss':[],
                        'phase':[] }
        
        attribute_dataframe = pd.read_csv(os.path.join(self.settings['project_path'], \
                    'GISCSVs',self.settings[name]['file_name']))
        
        columns = list(attribute_dataframe.columns)
        
        for keys,items in self.settings['transformer_column_mapper'].items():
            if keys in attribute_df:
                if items[0] == 'force': 
                    attribute_df[keys] = [items[1]]*len(attribute_dataframe)
                else:
                    if list(set(items)&set(columns)) != []:
                        attribute_df[keys] = list(attribute_dataframe[list(set(items)&set(columns))[0]])
        
        if self.settings["MVA_to_KVA_conversion_for_PT"] == "yes" and type != 'DTs': 
            attribute_df['KVA_cap'] = [el*1000 for el in attribute_df['KVA_cap']]
        
        if type == 'PTs':
            col,val = [],[]
            for keys,items in attribute_df.items():
                val.append(items[self.settings['PTrow']])
                col.append(keys)
            attribute_df = pd.DataFrame.from_dict({'0':val},orient='index',columns=col)
        else:
            attribute_df = pd.DataFrame.from_dict(attribute_df)
        
        attribute_df.to_csv(os.path.join(self.settings['project_path'], \
                self.settings['feeder_name'],csvname),index=False)
        
        self.logger.info('Exported "{}" file successfully'.format(csvname))
    
    
    def append_geometry(self,unique_geometry,tag):
    
        id = self.settings[tag]['phase_conductor']+'_'+str(self.settings[tag]['num_of_cond']) \
                + '_'+ self.settings[tag]['spacing']
        if id not in list(unique_geometry["ID"]):
            unique_geometry["ID"].append(id)
            for keys, items in self.settings[tag].items():
                unique_geometry[keys].append(items)
        return unique_geometry
        
    
    def export_linecsvs(self,line_or_cable,ht_or_lt,unique_geometry):

        
        name = '{}_{}'.format(ht_or_lt,line_or_cable)

        node_dataframe = pd.read_csv(os.path.join(self.settings['project_path'],'GISCSVs',
                    self.settings[name]['node_file_name']))
        
        attribute_dataframe = pd.read_csv(os.path.join(self.settings['project_path'], 'GISCSVs', \
                    self.settings[name]['attribute_file_name']))
        
        if 'wiredata.csv' in os.listdir(os.path.join(self.settings['project_path'],'ExtraCSVs')):
            wiredata = pd.read_csv(os.path.join(self.settings['project_path'],'ExtraCSVs','wiredata.csv'))
            cond_with_geom = list(wiredata.ID)

        node_df = {
            'shapeid' : list(node_dataframe.shapeid),
            'x' : list(node_dataframe.x),
            'y' : list(node_dataframe.y)
        }
        
        nodecsvname = '{}_{}_nodes.csv'.format(ht_or_lt,line_or_cable)
        
        node_df = pd.DataFrame.from_dict(node_df)
        
        node_df.to_csv(os.path.join(self.settings['project_path'],
                    self.settings['feeder_name'],nodecsvname),index=False)
        
        self.logger.info(f'Exported "{nodecsvname}" file successfully')

        attributecsvname = '{}_{}_attributes.csv'.format(ht_or_lt,line_or_cable)
        
        attribute_df = {'shapeid': [],
                        'length':[],
                        'phase':[],
                        'csize':[],
                        'num_of_cond':[],
                        'cname':[],
                        'spacing':[],
                        'units':[]}
        
        columns = list(attribute_dataframe.columns)
        
        attribute_df['shapeid'] = list(attribute_dataframe.shapeid)
        
        for keys,items in self.settings['line_column_mapper'].items():
            if keys in attribute_df:
                if items[0] == 'force': 
                    attribute_df[keys] = [items[1]]*len(attribute_dataframe)
                else:
                    if list(set(items)&set(columns)) != []:
                        attribute_df[keys] = list(attribute_dataframe[list(set(items)&set(columns))[0]])
        
        
        if list(set(self.settings["line_column_mapper"]["phase_system"])&set(columns)) != []:
            psys = list(attribute_dataframe[list(set(self.settings["line_column_mapper"] \
                        ["phase_system"])&set(columns))[0]])
            for el in psys:
                flag = 0
                if el in self.settings["line_column_mapper"]["four_conductor_system"]:
                    attribute_df['num_of_cond'].append(4)
                    flag = 1
                if el in self.settings["line_column_mapper"]["three_conductor_system"]:
                    attribute_df['num_of_cond'].append(3)
                    flag = 1
                if el in self.settings["line_column_mapper"]["two_conductor_system"]:
                    attribute_df['num_of_cond'].append(2)
                    flag =1
                if flag == 0:
                    attribute_df['num_of_cond'].append('NA')
        
        if self.settings['force_lt_be_three_phase'] == 'yes' and ht_or_lt == 'lt': 
            attribute_df['num_of_cond'] = [4]*len(attribute_dataframe)
        
        if list(set(self.settings['line_column_mapper']['nname'])&set(columns)) != []: 
            attribute_df['nname'] = list(attribute_dataframe[\
                list(set(self.settings['line_column_mapper']['nname'])&set(columns))[0]])
        
        if list(set(self.settings['line_column_mapper']['nsize'])&set(columns)) != []: 
            attribute_df['nsize'] = list(attribute_dataframe[\
                list(set(self.settings['line_column_mapper']['nsize'])&set(columns))[0]])       
        
        for id,val in enumerate(attribute_df['cname']):
            cond = attribute_df['cname'][id]+'_'+ str(attribute_df['csize'][id])
            if cond in cond_with_geom:
                geomid= cond + '_' + str(attribute_df['num_of_cond'][id])+'_'+ attribute_df['spacing'][id]
                if 'nname' in attribute_df:
                    geomid = geomid + '_'+ attribute_df['nname'][id]+'_'+ str(attribute_df['nsize'][id])
                if geomid not in list(unique_geometry['ID']):
                    unique_geometry['ID'].append(geomid)
                    spacing = self.settings['ht_spacing'] if ht_or_lt == 'ht' else self.settings['lt_spacing']
                    unique_geometry['conductor_spacing'].append(spacing)
                    num_of_phases = 3 if attribute_df['phase'][id] == self.settings['three_phase'] else 1
                    unique_geometry['num_of_phases'].append(num_of_phases)
                    unique_geometry['num_of_cond'].append(attribute_df['num_of_cond'][id])
                    height = self.settings['height_of_top_conductor_ht'] if ht_or_lt=='ht' \
                            else self.settings['height_of_top_conductor_lt']
                    unique_geometry['height_of_top_conductor'].append(height)
                    unique_geometry['phase_conductor'].append(cond)
                    if 'nname' not in attribute_df and attribute_df['num_of_cond'][id]>num_of_phases:
                        unique_geometry['neutral_conductor'].append(cond)
                    if 'nname' not in attribute_df and attribute_df['num_of_cond'][id]==num_of_phases:
                        unique_geometry['neutral_conductor'].append('NA')
                    if 'nname' in attribute_df:
                        unique_geometry['neutral_conductor'].append(attribute_df['nname'][id] \
                            +'_'+attribute_df['nsize'][id])
                    unique_geometry['units'].append(self.settings['geomtry_units'])
                    unique_geometry['spacing'].append(attribute_df['spacing'][id])
                
        attribute_df = pd.DataFrame.from_dict(attribute_df)
        
        attribute_df.to_csv(os.path.join(self.settings['project_path'], \
                self.settings['feeder_name'],attributecsvname),index=False)
        
        self.logger.info(f'Exported "{attributecsvname}" file successfully')
        
    def create_skeleton(self, project_path='.'):

        folder_list = ['GISCSVs','ExtraCSVs']
        for folder in folder_list:
            if folder not in os.listdir(project_path):
                os.mkdir(os.path.join(project_path,folder))
        
        with open(os.path.join(project_path,'config.json'),'w') as json_file:
            json.dump(DEFAULT_CONFIGURATION,json_file)

    def clear_folder(self,path):

        self.logger.info(f'Creating / cleaning folder: {path}')
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        for root, dirs, files in os.walk(path):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        return


if __name__ == '__main__':
    
    # #a = CSVFormatter({'project_path':r'C:\Users\KDUWADI\Desktop\NREL_Projects\
    # CIFF-TANGEDCO\TANGEDCO\EMERGE\Project_formatter',
    # #                    'feeder_name':'GWC'})
    isinstance = CSVFormatter()
    # isinstance.create_skeleton(r"C:\Users\KDUWADI\Desktop\NREL_Projects\
    # CIFF-TANGEDCO\TANGEDCO\EMERGE\Project_formatter\Test")
