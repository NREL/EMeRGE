# Standard imports
import shutil
import pathlib, os
import random
import pickle
import copy
from time import sleep
import sys
import math

# Third party imports
import networkx as nx
import pandas as pd
import numpy as np

# Internal imports

class Writer:

    def __init__(self,network, settings, logger, path, percen_consumer = 0.1, percen_pv = 1):
        
        self.settings = settings
        self.logger = logger
        self.logger.info('Writing OpenDSS files ............')

        self.nxgraph = network.nxgraph
        self.dss_files = []
        self.voltage_list =[]
        self.path = self.settings["project_path"]
        self.whichpath = path
        self.clear_folder()
        self.create_line_section()
        self.create_transformer()
        self.create_loads()
        self.create_bus_xy_file()
        if self.settings['include_PV'] == 'yes': self.create_pvsystems(percen_consumer,percen_pv)
        self.create_circuit()
        if settings['export_pickle_for_risk_analysis'] == 'yes':
            if not os.path.exists(os.path.join(settings['project_path'],'ExportedPickleFiles')):
                os.mkdir(os.path.join(settings['project_path'],'ExportedPickleFiles'))
                self.export_downcust_dict()
        self.logger.info('Writing DSS files completed successfully')


    def clear_folder(self):
        self.logger.info(f'Creating / cleaning folder: {self.whichpath}')
        pathlib.Path(self.whichpath).mkdir(parents=True, exist_ok=True)
        for root, dirs, files in os.walk(self.whichpath):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        return
    
    def create_line_section(self):

        # checking if condcutors are defined with proper csv name
        files = os.listdir(os.path.join(self.path,'ExtraCSVs'))
        def_cond = []
        if 'wiredata.csv' in files:
            wiredata = pd.read_csv(os.path.join(self.path,'ExtraCSVs','wiredata.csv'))
            def_cond.extend(list(wiredata.ID))
        if 'linecode.csv' in files:
            linecode = pd.read_csv(os.path.join(self.path,'ExtraCSVs','linecode.csv'))
            def_cond.extend(list(linecode.ID))
        if 'linegeometry.csv' in files:
            geometry = pd.read_csv(os.path.join(self.path,'ExtraCSVs','linegeometry.csv'))


        cond_type_size, unique_geo = [],[]
        index = 0
        self.lines = {}

        for node1,node2 in self.nxgraph.edges():
            edge_data = self.nxgraph[node1][node2]
            dss_dict = {}
            
            if edge_data['Type'] in ['HT_line','LT_line','HT_cable','LT_cable','Service_line']:
                self.nxgraph[node1][node2]['Name'] = self.modify_name(self.settings['feeder_name'] \
                                + edge_data['Type'] + '_' + str(index))
                tempname = edge_data['Cable type phase']+'_'+ str(edge_data['Cable size phase'])
                if tempname not in cond_type_size: cond_type_size.append(tempname)
                name = None
                if tempname in list(wiredata.ID): 
                    name = tempname+'_'+str(edge_data['num_of_cond'])+'_'+edge_data['spacing']
                if 'Cable size neutral' in edge_data:
                    tempname = edge_data['Cable type neutral']+'_'+ str(edge_data['Cable size neutral'])
                    if tempname not in cond_type_size: cond_type_size.append(tempname)
                    if name != None:
                        name = name + '_' + tempname
                if name not in unique_geo and name != None:
                    unique_geo.append(name)
                
                if edge_data['Phase_con'] == self.settings["three_phase"]:
                    code = '.1.2.3' if edge_data['num_of_cond'] == 3 else '.1.2.3.0'
                else:
                    code = '.' + str(self.settings['phase2num'][edge_data['Phase_con']])+'.0'
                
                dss_dict['bus1'] = self.modify_name(node1) + code
                dss_dict['bus2'] = self.modify_name(node2) + code
                dss_dict['length'] = edge_data['Length']

                if tempname in list(wiredata.ID):
                    dss_dict['geometry'] = self.modify_name(name)
                if tempname in list(linecode.ID):
                    dss_dict['linecode'] = self.modify_name(tempname)

                dss_dict['units'] = edge_data['units']
                dss_dict['enabled'] = 'True'

                self.lines[self.modify_name(edge_data['Name'])] =  dss_dict

                
                if edge_data['Type'] in ['LT_line','LT_cable']:
                    if self.settings['multi_threephase_for_lt'] == 'yes' \
                                and self.settings['num_of_parallel_three_phase']>1:
                        for i in range(self.settings['num_of_parallel_three_phase']-1):
                            self.lines[self.modify_name(edge_data['Name']+'_'+str(i+1))] =  dss_dict

                index+=1

        for el in cond_type_size:
            assert el in def_cond, 'Conductor {} with size {} is not defined in \
                        either of wiredata.csv or linecode.csv'.format(el.split('_')[0],el.split('_')[1])

        for el in unique_geo:
            assert el in list(geometry.ID), 'Conductor geometry {} is not defined in linegeometry.csv'.format(el)

        if 'wiredata.csv' in files: self.createwiredss(wiredata)
        if 'linecode.csv' in files: self.createlinecodedss(linecode)
        if 'linegeometry.csv' in files: self.createlinegeometrydss(geometry)
        self.to_dss('line',self.lines)
    

    def create_transformer(self):

        index = 0
        self.transformer = {}
        for node1,node2 in self.nxgraph.edges():
            edge_data = self.nxgraph[node1][node2]
            dss_dict = {}
            if edge_data['Type'] in ['DTs','PTs']:
                self.nxgraph[node1][node2]['Name']  = self.modify_name(self.settings['feeder_name'] \
                                + edge_data['Type'] + '_' + str(index))
                dss_dict['phases'] = 3 if edge_data['phase'] == self.settings['three_phase'] else 1
                dss_dict['windings'] = 2
                
                if edge_data['Type'] == 'DTs':
                    hv_node = node1 if self.nxgraph.node[node1]['Type'] == 'HTnode' else node2
                else:
                    hv_node = node2 if self.nxgraph.node[node1]['Type'] == 'HTnode' else node1
                    self.ssnode = hv_node

                lv_node = node1 if hv_node==node2 else node2
                if edge_data['phase'] == self.settings['three_phase']:
                    hv_node = self.modify_name(hv_node) + '.1.2.3' if edge_data['prim_con'] == 'delta' \
                                else self.modify_name(hv_node) + '.1.2.3.0'
                    lv_node = self.modify_name(lv_node) + '.1.2.3' if edge_data['sec_con'] == 'delta' \
                        else self.modify_name(lv_node) + '.1.2.3.0'
                else:
                    hv_node = self.modify_name(hv_node) + '.'+ str(self.settings['num2phase'][edge_data['phase']])
                    lv_node = self.modify_name(lv_node) + '.'+ str(self.settings['num2phase'][edge_data['phase']])

                if edge_data['Type'] == 'PTs': 
                    self.swing = hv_node
                    self.metername = self.nxgraph[node1][node2]['Name']
                
                dss_dict['buses'] = '[{},{}]'.format(hv_node,lv_node)
                dss_dict['conns'] = '[{},{}]'.format(edge_data['prim_con'],edge_data['sec_con'])
                dss_dict['kvs'] = '[{},{}]'.format(edge_data['HV_KV'],edge_data['LV_KV'])
                if edge_data['HV_KV'] not in self.voltage_list: self.voltage_list.append(edge_data['HV_KV'])
                if edge_data['LV_KV'] not in self.voltage_list: self.voltage_list.append(edge_data['LV_KV'])
                dss_dict['kvas'] = '[{},{}]'.format(edge_data['KVA_cap'],edge_data['KVA_cap'])
                dss_dict['xhl'] = edge_data['%reactance']
                dss_dict['%noloadloss'] = edge_data['%noloadloss']
                dss_dict['%r'] = edge_data['%resistance']
                dss_dict['maxtap'] = edge_data['maxtap']
                dss_dict['mintap'] = edge_data['mintap']
                dss_dict['tap'] = edge_data['tap']
                dss_dict['numtaps'] = edge_data['numtaps']
                if edge_data['phase'] == self.settings['three_phase'] and edge_data['vector_group'] == 'Dyn11':
                    dss_dict['leadlag'] = 'lead'
                index+=1
                self.transformer[edge_data['Name']] = dss_dict
        
        self.to_dss('transformer',self.transformer)
    
    def create_loads(self):

        self.load = {}
        self.load_tec = {}
        self.uniquecusttype = []
        for node in self.nxgraph.nodes():
            nodedata = self.nxgraph.node[node]
            if 'loads' in nodedata:
                for keys, values in nodedata['loads'].items():
                    if values['phase'] == self.settings['three_phase']:
                        bus1code = '.1.2.3' if values['load_type'] == 'delta' else '.1.2.3.0'
                    else:
                        bus1code = '.' + str(self.settings['phase2num'][values['phase']]) + '.0'
                    dss_dict = {
                        'phases' : 3 if values['phase'] == self.settings['three_phase'] else 1,
                        'bus1' : self.modify_name(node) + bus1code,
                        'kv'   : values['kv'],
                        'kw'   : values['kw'],
                        'pf'   : values['pf'],
                        'conn' : values['load_type'],
                    }
                    if values['kv'] not in self.voltage_list: self.voltage_list.append(values['kv'])
                    if self.settings['time_series_pf'] == 'yes':
                        dss_dict['yearly'] = values['con_type']
                        if values['con_type'] not in self.uniquecusttype: 
                            self.uniquecusttype.append(values['con_type'])
                    
                    if 'tec' in values :self.load_tec[self.modify_name(str(keys))] = values['tec'] 
                    self.load[self.modify_name(str(keys))] = dss_dict
        
        if self.settings['time_series_pf'] == 'yes': self.create_loadshape()
        self.to_dss('load',self.load)
    
    def create_pvsystems(self,percen_consumer,percen_pv):

        # first find out potential consumer for PV inter-connection
        potential_pv_customers = []
        for keys, values in self.load.items():
            if values['kv'] in self.settings['PV_volt_label']:
                potential_pv_customers.append(keys)
        
        dist_array = []
        for k in potential_pv_customers:
            sx,sy = float(self.ssnode.split('_')[0]),float(self.ssnode.split('_')[1])
            nodename = self.load[k]['bus1']
            x,y = float(nodename.split('_')[0].replace('-','.')),float(nodename.split('_')[1].replace('-','.'))
            dist_array.append(math.sqrt((sx-x)**2+(sy-y)**2))
        d_array = [math.exp(-k) for k in dist_array]
        dd_array = [1-k/sum(d_array) for k in d_array] 
        ddd_array = [k/sum(dd_array) for k in dd_array]# assigning higher probabilities to farther PV
        pv_customers = np.random.choice(potential_pv_customers, \
                int(percen_consumer*len(potential_pv_customers)),replace=False,p=ddd_array)   

        #PV_customers = list(random.sample(set(potential_PV_customers), int(percen_consumer*len(potential_PV_customers)))

        if self.settings['export_pickle_for_risk_analysis'] == 'yes':
            if os.path.exists(os.path.join(self.settings['project_path'],'ExportedcoordCSVs')) != True:
                os.mkdir(os.path.join(self.settings['project_path'],'ExportedcoordCSVs'))
            pv_dict = {'component_name':[],'x':[],'y':[]}
            for k in pv_customers:
                pv_dict['component_name'].append(self.modify_name(k+'PV'))
                nodename = self.load[k]['bus1']
                x,y = float(nodename.split('_')[0].replace('-','.')),float(nodename.split('_')[1].replace('-','.'))
                pv_dict['x'].append(x)
                pv_dict['y'].append(y)
            df = pd.DataFrame.from_dict(pv_dict)
            csvname = str(percen_consumer*100)+'%customer-'+ str(percen_pv*100) +'%-PV.csv' \
                                if percen_pv !=0 else 'Base.csv'
            df.to_csv(os.path.join(self.settings['project_path'],'ExportedcoordCSVs',csvname ))

        self.pv_system = {}
        for cust in pv_customers:
            dss_dict = {
                'bus1' : self.load[cust]['bus1'],
                'phases' : self.load[cust]['phases'],
                'kv' : self.load[cust]['kv'],
                'kva' : percen_pv*self.load_tec[cust]*self.settings['inverter_oversize_factor'] \
                                /(365*24*self.settings['annual_PV_capacity_factor']),
                'irradiance' : self.settings['max_pu_irradiance'],
                'pmpp': percen_pv*self.load_tec[cust]/(365*24*self.settings['annual_PV_capacity_factor']),
                'kvar': 0 if self.settings['no_reactive_support_from_PV'] == "yes" else 0,
                '%cutin': self.settings['PV_cutin'],
                '%cutout': self.settings['PV_cutout'],
            }
            if self.settings['time_series_pf'] == 'yes':
                dss_dict['yearly'] = self.settings['solar_csvname'].split('.csv')[0]
            self.pv_system[cust+'PV'] = dss_dict
        self.to_dss('PVsystem',self.pv_system)

    def create_loadshape(self):
        
        files = os.listdir(os.path.join(self.path,'ExtraCSVs'))
        if self.settings['include_PV']: 
            self.uniquecusttype.append(self.settings['solar_csvname'].split('.csv')[0])
            assert self.settings['solar_csvname'] in files, '{} doesnot exist in \
                        "ExtraCSVs" folder'.format(self.settings['solar_csvname'])
        if self.settings['time_series_voltage_profile'] == 'yes': 
            self.uniquecusttype.append(self.settings['voltage_csv_name'].split('.csv')[0])
            assert self.settings['voltage_csv_name'] in files, '{} doesnot exist \
                    in "ExtraCSVs" folder'.format(self.settings['voltage_csv_name'])
        self.loadshape = {}

        
        for el in self.uniquecusttype:
            dss_dict = {
                'npts' : self.settings['num_of_data_points'],
                'minterval' : self.settings['minute-interval'],
                'mult': '(file='+ str(el) + '.csv)',
            }
            assert str(el.lower())+'.csv' in files, '{} doesnot exist \
                    in "ExtraCSVs" folder'.format(str(el.lower())+'.csv')
            self.loadshape[self.modify_name(el)] = dss_dict
            shutil.copy(os.path.join(self.path,'ExtraCSVs',str(el.lower())+'.csv'), self.whichpath)
            
        self.to_dss('loadshape',self.loadshape)
    
    def create_circuit(self):

        self.logger.info('Writing File - ' + self.modify_name(self.settings['feeder_name']) + '.dss')
        file = open(self.whichpath + '/' + self.modify_name(self.settings['feeder_name']) + '.dss', 'w')
        file.write('clear\n\n')
        if 'loadshape.dss' in self.dss_files:
            file.write('redirect ' + 'loadshape.dss' + '\n\n')
        file.write('New circuit.' + self.modify_name(self.settings['feeder_name']).lower() + '\n')
        
        if self.settings['time_series_voltage_profile'] == 'yes' and self.settings['time_series_pf'] == 'yes':
            file.write('~ basekv={0} basefreq={1} pu={2} phases={3} Z1={4} Z0= {5} bus1={6} yearly={7}\n'\
                    .format(self.settings['sourcebasekv'],self.settings['sourcebasefreq'],
                    self.settings['sourcepu'],self.settings['source_num_of_phase'],
                    self.settings['sourceposseq_impedance'],self.settings['sourcezeroseq_impedance'],
                    self.swing,self.settings['voltage_csv_name'].split('.csv')[0]))
        else:
            file.write('~ basekv={0} basefreq={1} pu={2} phases={3} Z1={4} Z0= {5} bus1={6}\n'\
                .format(self.settings['sourcebasekv'],self.settings['sourcebasefreq'],self.settings['sourcepu'],
                self.settings['source_num_of_phase'],self.settings['sourceposseq_impedance'],
                self.settings['sourcezeroseq_impedance'],self.swing))
        for filename in self.dss_files:
            if filename != 'loadshape.dss':
                file.write('redirect ' + filename.lower() + '\n\n')
        file.write('Set voltagebases={}\n\n'.format(self.voltage_list))
        file.write('Calcv\n\n')
        file.write('new energymeter.vol ' + 'transformer.'+ self.metername + '\n\n')
        if self.settings['time_series_pf'] == 'yes':
            file.write('set mode = yearly\n\n')
            file.write('set stepsize = 15m\n\n')
        file.write('BusCoords ' + self.coord_filename  + '\n\n')
        if self.settings['time_series_pf'] != 'yes':
            file.write('solve\n\n')
            file.write('plot circuit\n\n')
            file.write('plot profile\n\n')
        file.close()
        
    def createwiredss(self,wiredata):
        self.wire_info = {}
        for i in range(len(wiredata)):
            dss_dict = {
               'diam' : wiredata.Diameter[i],
               'GMRac' : wiredata.GMRAC[i],
               'GMRunits' : wiredata.GMRunits[i],
               'normamps' : wiredata.normamps[i],
               'Rac'   : wiredata.Rac[i],
               'Runits' : wiredata.Runits[i],
               'radunits' : wiredata.Radunits[i],
            }
            self.wire_info[self.modify_name(wiredata.ID[i])] = dss_dict
        self.to_dss('wiredata', self.wire_info)
    
    def createlinecodedss(self,linecode):
        self.linecode_info = {}
        for i in range(len(linecode)):
            dss_dict = {
               'nphases' : linecode.num_of_phases[i],
               'r0' : linecode.r0[i],
               'r1' : linecode.r1[i],
               'x0' : linecode.x0[i],
               'x1'   : linecode.x1[i],
               'c0' : linecode.c0[i],
               'c1' : linecode.c1[i],
               'units' : linecode.units[i]
            }
            self.linecode_info[self.modify_name(linecode.ID[i])] = dss_dict
        self.to_dss('linecode', self.linecode_info)
    
    def createlinegeometrydss(self,geometry):
        self.linegeometry_info = {}
        for i in range(len(geometry)):

            reduce = 'no' if geometry.num_of_cond[i] == geometry.num_of_phases[i] else 'yes'
                
            dss_dict = {
               'nconds' : geometry.num_of_cond[i],
               'nphases' : geometry.num_of_phases[i],
               'reduce' : reduce,
            }
            for k in range(geometry.num_of_cond[i]):

                if geometry.spacing[i] == 'vertical':
                    x = geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k-1) \
                                if geometry.num_of_cond[i]>geometry.num_of_phases[i] \
                                else geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k)
                    h = geometry.height_of_top_conductor[i] - k*geometry.conductor_spacing[i] 
                
                if geometry.spacing[i] == 'horizontal':
                    x = geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k-1) \
                            if geometry.num_of_cond[i]>geometry.num_of_phases[i] \
                            else geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k)
                    h = geometry.height_of_top_conductor[i]
                
                assert geometry.spacing[i] in ['vertical', 'horizontal'], 'new spacing {} \
                        not defined in the program'.format(geometry.spacing[i])
                dss_dict['cond'+str(k+1)] = {
                    'cond': k+1, 
                    'wire': self.modify_name(geometry.phase_conductor[i]),
                    'x': x,
                    'h': h,
                    'units': geometry.units[i],
                }
            if geometry.num_of_cond[i] > geometry.num_of_phases[i]:
                dss_dict['cond'+str(geometry.num_of_cond[i])]['wire'] = self.modify_name(geometry.neutral_conductor[i])


            self.linegeometry_info[self.modify_name(geometry.ID[i])] = dss_dict
        self.to_dss('linegeometry', self.linegeometry_info)


    def to_dss(self, element_type, info_dict):
        if '_' in element_type:
            elm_type = element_type.split('_')[1]
            file_name = element_type.split('_')[0]
        else:
            elm_type = element_type
            file_name = element_type
        
        self.logger.info('Writing FIle -' + file_name + '.dss')
        path = self.whichpath
        is_dict = 0
        file = open(path + '/' + file_name + '.dss', 'w')
        self.dss_files.append(file_name + '.dss')
        for name, properties in info_dict.items():
            new_cmd = 'New '+ elm_type + '.' + name + ' '
            for prop_name, prop_value in properties.items():
                if isinstance(prop_value,dict):
                    file.write(new_cmd.lower()+'\n')
                    is_dict = 1
                    new_cmd = '~ '
                    for key, value in prop_value.items():
                         new_cmd += key + '=' + str(value) + ' '
                else:
                    new_cmd += prop_name + '=' + str(prop_value ) + ' '
            if is_dict == 0:
                file.write(new_cmd.lower()+'\n')
            else:
                file.write(new_cmd.lower()+'\n')
            file.write('\n')
        file.close()
    
    def create_bus_xy_file(self):
        self.logger.info('Writing File - Bus_Coordinates.csv')
        file = open(self.whichpath + '/Bus_Coordinates.csv', 'w')
        nodes = self.nxgraph.nodes()
        for node in nodes:
            node_attrs = self.nxgraph.node[node]
            if 'x' in node_attrs and 'y' in node_attrs:
                X = node_attrs['x']
                Y = node_attrs['y']
                file.write(self.modify_name(node) + ', ' + str(X) + ', ' + str(Y) + '\n')
        file.close()
        self.coord_filename = 'Bus_Coordinates.csv'
        return
    
    def modify_name(self, name):
        invalid_chars = [' ', ',', '.']
        for inv_char in invalid_chars:
            if inv_char in name:
                name = name.replace(inv_char,'-')
        name = name.lower()
        return name
    
    def export_downcust_dict(self):  
        
        line_cust_down = {key:[] for key in self.lines.keys()}
        line_coords = {'component_name':[],'x1':[],'y1':[],'x2':[],'y2':[]}
        index,counter = 0,0
        self.logger.info('Please wait untill "line_cust_dict.p" and "line_coords.csv" files are being exported .....>>>>')
        for node1,node2 in self.nxgraph.edges():
            edge_data = self.nxgraph[node1][node2]
            if edge_data['Type'] in ['HT_line','LT_line','HT_cable','LT_cable','Service_line']:
                name  = self.modify_name(self.settings['feeder_name'] + edge_data['Type'] + '_' + str(index))
                assert name in line_cust_down,'{} not present in dss files'.format(name)
                temp_network = copy.deepcopy(self.nxgraph)
                temp_network.remove_edge(node1,node2)
                islands = list(nx.connected_component_subgraphs(temp_network))
                cust_down = []
                for i in range(len(islands)):
                    if islands[i].has_node(self.ssnode) != True:
                        for n in islands[i].nodes():
                            if 'loads' in islands[i].node[n]:
                                cust_down.append(self.modify_name(list(islands[i].node[n]['loads'])[0]))
                line_coords['component_name'].append(name)
                line_coords['x1'].append(self.nxgraph.node[node1]['x'])
                line_coords['y1'].append(self.nxgraph.node[node1]['y'])
                line_coords['x2'].append(self.nxgraph.node[node2]['x'])
                line_coords['y2'].append(self.nxgraph.node[node2]['y'])               
                line_cust_down[name]  = cust_down
                counter+=1
                if edge_data['Type'] in ['LT_line','LT_cable']:
                    if self.settings['multi_threephase_for_lt'] == 'yes' \
                            and self.settings['num_of_parallel_three_phase']>1:
                        for i in range(self.settings['num_of_parallel_three_phase']-1):
                            name = self.modify_name(self.modify_name(self.settings['feeder_name'] \
                                        + edge_data['Type'] + '_' + str(index))+'_'+str(i+1))
                            assert name in line_cust_down,'{} not present in dss files'.format(name) 
                            line_cust_down[name]  = cust_down
                            line_coords['component_name'].append(name)
                            line_coords['x1'].append(self.nxgraph.node[node1]['x'])
                            line_coords['y1'].append(self.nxgraph.node[node1]['y'])
                            line_coords['x2'].append(self.nxgraph.node[node2]['x'])
                            line_coords['y2'].append(self.nxgraph.node[node2]['y'])  
                            counter +=1
                
                index+=1
                print("\r[%-100s] %d%%" % ('>'*int(counter*100/len(line_cust_down)), \
                        int(counter*100/len(line_cust_down))),end='')
        pickle.dump(line_cust_down,open(os.path.join(self.settings['project_path'],\
                    'ExportedPickleFiles','line_cust_down.p'),"wb"))
        df = pd.DataFrame.from_dict(line_coords)
        df.to_csv(os.path.join(self.settings['project_path'],\
                'ExportedcoordCSVs','line_coords.csv'))
        self.logger.info('\n line_cust_dict.p and line_coords.csv files exported successfully')

        ## Export for transformer
        transformer_coords = {'component_name':[],'x':[],'y':[]}
        transformer_cust_down = {key:[] for key in self.transformer.keys()}
        index = 0
        self.logger.info('Please wait untill "transformer_cust_dict.p" and "transformers_coords.csv' 
            'files are being exported .....>>>>')
        
        for node1,node2 in self.nxgraph.edges():
            edge_data = self.nxgraph[node1][node2]
            if edge_data['Type'] in ['DTs','PTs']:
                name  = self.modify_name(self.settings['feeder_name'] + edge_data['Type'] + '_' + str(index))
                if name in transformer_cust_down:
                    temp_network = copy.deepcopy(self.nxgraph)
                    temp_network.remove_edge(node1,node2)
                    islands = list(nx.connected_component_subgraphs(temp_network))
                    cust_down = []
                    for i in range(len(islands)):
                        if islands[i].has_node(self.ssnode) != True:
                            for n in islands[i].nodes():
                                if 'loads' in islands[i].node[n]:
                                    cust_down.append(self.modify_name(list(islands[i].node[n]['loads'])[0]))
                
                transformer_cust_down[name]  = cust_down
                transformer_coords['component_name'].append(name)
                transformer_coords['x'].append((self.nxgraph.node[node1]['x']+self.nxgraph.node[node2]['x'])/2)
                transformer_coords['y'].append((self.nxgraph.node[node1]['y']+self.nxgraph.node[node2]['y'])/2)
                index+=1
                print("\r[%-100s] %d%%" % ('>'*int(index*100/len(transformer_cust_down)), \
                            int(index*100/len(transformer_cust_down))),end='')
        pickle.dump(transformer_cust_down,open(os.path.join(self.settings['project_path'],\
                    'ExportedPickleFiles','transformer_cust_down.p'),"wb"))
        df = pd.DataFrame.from_dict(transformer_coords)
        df.to_csv(os.path.join(self.settings['project_path'],'ExportedcoordCSVs','transformer_coords.csv'))
        self.logger.info('\n transformer_cust_dict.p and transformer_coords.csv files exported successfully')

        # Export for buses

        node_cust_dict = {}
        node_coords = {'component_name':[],'x':[],'y':[]}
        counter = 0
        self.logger.info('Please wait untill "node_cust_dict.p" and "node_coords.p" files are being exported .....>>>>')
        for node in self.nxgraph.nodes():
            temp_network = copy.deepcopy(self.nxgraph)
            temp_network.remove_node(node)
            islands = list(nx.connected_component_subgraphs(temp_network))
            cust_down = []
            no_nodes_list = []
            for i in range(len(islands)):
                if islands[i].has_node(self.ssnode) == True:
                    no_nodes_list = islands[i].nodes()
            
            for N2 in temp_network.nodes():
                if 'loads' in temp_network.node[N2] and N2 not in no_nodes_list:
                    cust_down.append(self.modify_name(list(temp_network.node[N2]['loads'])[0]))
            
            node_cust_dict[self.modify_name(node)] = cust_down
            node_coords['component_name'].append(self.modify_name(node))
            node_coords['x'].append(self.nxgraph.node[node]['x'])
            node_coords['y'].append(self.nxgraph.node[node]['y'])
        
            counter+=1
            print("\r[%-100s] %d%%" % ('>'*int(counter*100/len(self.nxgraph.nodes())), \
                int(counter*100/len(self.nxgraph.nodes()))),end='')
        pickle.dump(node_cust_dict,open(os.path.join(self.settings['project_path'], \
                'ExportedPickleFiles','node_cust_down.p'),"wb"))
        df = pd.DataFrame.from_dict(node_coords)
        df.to_csv(os.path.join(self.settings['project_path'],'ExportedcoordCSVs','node_coords.csv'))
        self.logger.info('\n node_cust_dict.p and node_coords.csv file exported successfully')
    