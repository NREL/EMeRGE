import networkx as nx
import pandas as pd
import numpy as np
import shutil
import pathlib, os
import random
import pickle
import copy
from time import sleep
import sys
import math

class Writer:

    def __init__(self,network, settings,path, percen_consumer = 0.1, percen_pv = 1):
        print('Writing OpenDSS files ............')
        self.__nxGraph = network.NXgraph
        self.__DSSfiles = []
        self.__voltage_collec =[]
        self.__settings = settings
        self.path = self.__settings["Project path"]
        self.__whichpath = path
        self.__ClearProjectFolder()
        self.__Create_Line_section()
        self.__Create_Transformer()
        self.__Create_loads()
        self.__CreateBusXYFile()
        if self.__settings['include_PV'] == 'yes': self.__Create_PVsystems(percen_consumer,percen_pv)
        self.__CreateCircuit()
        if settings['export_pickle_for_risk_analysis'] == 'yes':
            if not os.path.exists(os.path.join(settings['Project path'],'ExportedPickleforRiskAnalysis')):
                os.mkdir(os.path.join(settings['Project path'],'ExportedPickleforRiskAnalysis'))
                self.__export_downcust_dict()
        print('Writing DSS files completed successfully')


    def __ClearProjectFolder(self):
        print('Creating / cleaning folder: ',  self.__whichpath)
        pathlib.Path(self.__whichpath).mkdir(parents=True, exist_ok=True)
        for root, dirs, files in os.walk(self.__whichpath):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))
        return
    
    def __Create_Line_section(self):

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
        self.Lines = {}

        for node1,node2 in self.__nxGraph.edges():
            edgeData = self.__nxGraph[node1][node2]
            dssDict = {}
            
            if edgeData['Type'] in ['HT_line','LT_line','HT_cable','LT_cable','Service_line']:
                self.__nxGraph[node1][node2]['Name']  = self.__ModifyName(self.__settings['Feeder name'] + edgeData['Type'] + '_' + str(index))
                tempname = edgeData['Cable type phase']+'_'+ str(edgeData['Cable size phase'])
                if tempname not in cond_type_size: cond_type_size.append(tempname)
                name = None
                if tempname in list(wiredata.ID): 
                    name = tempname+'_'+str(edgeData['num_of_cond'])+'_'+edgeData['spacing']
                if 'Cable size neutral' in edgeData:
                    tempname = edgeData['Cable type neutral']+'_'+ str(edgeData['Cable size neutral'])
                    if tempname not in cond_type_size: cond_type_size.append(tempname)
                    if name != None:
                        name = name + '_' + tempname
                if name not in unique_geo and name != None:
                    unique_geo.append(name)
                
                if edgeData['Phase_con'] == self.__settings["three_phase"]:
                    code = '.1.2.3' if edgeData['num_of_cond'] == 3 else '.1.2.3.0'
                else:
                    code = '.' + str(self.__settings['phase2num'][edgeData['Phase_con']])+'.0'
                
                dssDict['bus1'] = self.__ModifyName(node1) + code
                dssDict['bus2'] = self.__ModifyName(node2) + code
                dssDict['length'] = edgeData['Length']

                if tempname in list(wiredata.ID):
                    dssDict['geometry'] = self.__ModifyName(name)
                if tempname in list(linecode.ID):
                    dssDict['linecode'] = self.__ModifyName(tempname)

                dssDict['units'] = edgeData['units']
                dssDict['enabled'] = 'True'

                self.Lines[self.__ModifyName(edgeData['Name'])] =  dssDict

                
                if edgeData['Type'] in ['LT_line','LT_cable']:
                    if self.__settings['multi_threephase_for_lt'] == 'yes' and self.__settings['num_of_parallel_three_phase']>1:
                        for i in range(self.__settings['num_of_parallel_three_phase']-1):
                            self.Lines[self.__ModifyName(edgeData['Name']+'_'+str(i+1))] =  dssDict

                index+=1

        for el in cond_type_size:
            assert el in def_cond, 'Conductor {} with size {} is not defined in either of wiredata.csv or linecode.csv'.format(el.split('_')[0],el.split('_')[1])

        for el in unique_geo:
            assert el in list(geometry.ID), 'Conductor geometry {} is not defined in linegeometry.csv'.format(el)

        if 'wiredata.csv' in files: self.__createwiredss(wiredata)
        if 'linecode.csv' in files: self.__createlinecodedss(linecode)
        if 'linegeometry.csv' in files: self.__createlinegeometrydss(geometry)
        self.__toDSS('line',self.Lines)
    

    def __Create_Transformer(self):

        index = 0
        self.Transformer = {}
        for node1,node2 in self.__nxGraph.edges():
            edgeData = self.__nxGraph[node1][node2]
            dssDict = {}
            if edgeData['Type'] in ['DTs','PTs']:
                self.__nxGraph[node1][node2]['Name']  = self.__ModifyName(self.__settings['Feeder name'] + edgeData['Type'] + '_' + str(index))
                dssDict['phases'] = 3 if edgeData['phase'] == self.__settings['three_phase'] else 1
                dssDict['windings'] = 2
                
                if edgeData['Type'] == 'DTs':
                    hv_node = node1 if self.__nxGraph.node[node1]['Type'] == 'HTnode' else node2
                else:
                    hv_node = node2 if self.__nxGraph.node[node1]['Type'] == 'HTnode' else node1
                    self.ssnode = hv_node

                lv_node = node1 if hv_node==node2 else node2
                if edgeData['phase'] == self.__settings['three_phase']:
                    hv_node = self.__ModifyName(hv_node) + '.1.2.3' if edgeData['prim_con'] == 'delta' else self.__ModifyName(hv_node) + '.1.2.3.0'
                    lv_node = self.__ModifyName(lv_node) + '.1.2.3' if edgeData['sec_con'] == 'delta' else self.__ModifyName(lv_node) + '.1.2.3.0'
                else:
                    hv_node = self.__ModifyName(hv_node) + '.'+ str(self.__settings['num2phase'][edgeData['phase']])
                    lv_node = self.__ModifyName(lv_node) + '.'+ str(self.__settings['num2phase'][edgeData['phase']])

                if edgeData['Type'] == 'PTs': 
                    self.swing = hv_node
                    self.metername = self.__nxGraph[node1][node2]['Name']
                dssDict['buses'] = '[{},{}]'.format(hv_node,lv_node)
                dssDict['conns'] = '[{},{}]'.format(edgeData['prim_con'],edgeData['sec_con'])
                dssDict['kvs'] = '[{},{}]'.format(edgeData['HV_KV'],edgeData['LV_KV'])
                if edgeData['HV_KV'] not in self.__voltage_collec: self.__voltage_collec.append(edgeData['HV_KV'])
                if edgeData['LV_KV'] not in self.__voltage_collec: self.__voltage_collec.append(edgeData['LV_KV'])
                dssDict['kvas'] = '[{},{}]'.format(edgeData['KVA_cap'],edgeData['KVA_cap'])
                dssDict['xhl'] = edgeData['%reactance']
                dssDict['%noloadloss'] = edgeData['%noloadloss']
                dssDict['%r'] = edgeData['%resistance']
                dssDict['maxtap'] = edgeData['maxtap']
                dssDict['mintap'] = edgeData['mintap']
                dssDict['tap'] = edgeData['tap']
                dssDict['numtaps'] = edgeData['numtaps']
                if edgeData['phase'] == self.__settings['three_phase'] and edgeData['vector_group'] == 'Dyn11':
                    dssDict['leadlag'] = 'lead'
                index+=1
                self.Transformer[edgeData['Name']] = dssDict
        
        self.__toDSS('transformer',self.Transformer)
    
    def __Create_loads(self):

        self.__Load = {}
        self.__loadTEC = {}
        self.__uniquecusttype = []
        for node in self.__nxGraph.nodes():
            nodedata = self.__nxGraph.node[node]
            if 'loads' in nodedata:
                for keys, values in nodedata['loads'].items():
                    if values['phase'] == self.__settings['three_phase']:
                        bus1code = '.1.2.3' if values['load_type'] == 'delta' else '.1.2.3.0'
                    else:
                        bus1code = '.' + str(self.__settings['phase2num'][values['phase']]) + '.0'
                    dssDict = {
                        'phases' : 3 if values['phase'] == self.__settings['three_phase'] else 1,
                        'bus1' : self.__ModifyName(node) + bus1code,
                        'kv'   : values['kv'],
                        'kw'   : values['kw'],
                        'pf'   : values['pf'],
                        'conn' : values['load_type'],
                    }
                    if values['kv'] not in self.__voltage_collec: self.__voltage_collec.append(values['kv'])
                    if self.__settings['time_series_pf'] == 'yes':
                        dssDict['yearly'] = values['con_type']
                        if values['con_type'] not in self.__uniquecusttype: self.__uniquecusttype.append(values['con_type'])
                    
                    if 'tec' in values :self.__loadTEC[self.__ModifyName(str(keys))] = values['tec'] 
                    self.__Load[self.__ModifyName(str(keys))] = dssDict
        
        if self.__settings['time_series_pf'] == 'yes': self.__Create_loadshape()
        self.__toDSS('load',self.__Load)
    
    def __Create_PVsystems(self,percen_consumer,percen_PV):

        # first find out potential consumer for PV inter-connection
        potential_PV_customers = []
        for keys, values in self.__Load.items():
            if values['kv'] in self.__settings['PV_volt_label']:
                potential_PV_customers.append(keys)
        
        
        dist_array = []
        for k in potential_PV_customers:
            sx,sy = float(self.ssnode.split('_')[0]),float(self.ssnode.split('_')[1])
            nodename = self.__Load[k]['bus1']
            x,y = float(nodename.split('_')[0].replace('-','.')),float(nodename.split('_')[1].replace('-','.'))
            dist_array.append(math.sqrt((sx-x)**2+(sy-y)**2))
        d_array = [math.exp(-k) for k in dist_array]
        dd_array = [1-k/sum(d_array) for k in d_array] 
        ddd_array = [k/sum(dd_array) for k in dd_array]# assigning higher probabilities to farther PV
        PV_customers = np.random.choice(potential_PV_customers,int(percen_consumer*len(potential_PV_customers)),replace=False,p=ddd_array)   

        #PV_customers = list(random.sample(set(potential_PV_customers), int(percen_consumer*len(potential_PV_customers)))

        if self.__settings['export_pickle_for_risk_analysis'] == 'yes':
            if os.path.exists(os.path.join(self.__settings['Project path'],'ExportedcoordCSVs')) != True: os.mkdir(os.path.join(self.__settings['Project path'],'ExportedcoordCSVs'))
            PV_dict = {'component_name':[],'x':[],'y':[]}
            for k in PV_customers:
                PV_dict['component_name'].append(self.__ModifyName(k+'PV'))
                nodename = self.__Load[k]['bus1']
                x,y = float(nodename.split('_')[0].replace('-','.')),float(nodename.split('_')[1].replace('-','.'))
                PV_dict['x'].append(x)
                PV_dict['y'].append(y)
            df = pd.DataFrame.from_dict(PV_dict)
            csvname = str(percen_consumer*100)+'%customer-'+ str(percen_PV*100) +'%-PV.csv' if percen_PV !=0 else 'Base.csv'
            df.to_csv(os.path.join(self.__settings['Project path'],'ExportedcoordCSVs',csvname ))

        self.__PVSystem = {}
        for cust in PV_customers:
            dssDict = {
                'bus1' : self.__Load[cust]['bus1'],
                'phases' : self.__Load[cust]['phases'],
                'kv' : self.__Load[cust]['kv'],
                'kva' : percen_PV*self.__loadTEC[cust]*self.__settings['inverter_oversize_factor']/(365*24*self.__settings['annual_PV_capacity_factor']),
                'irradiance' : self.__settings['max_pu_irradiance'],
                'pmpp': percen_PV*self.__loadTEC[cust]/(365*24*self.__settings['annual_PV_capacity_factor']),
                'kvar': 0 if self.__settings['no_reactive_support_from_PV'] == "yes" else 0,
                '%cutin': self.__settings['PV_cutin'],
                '%cutout': self.__settings['PV_cutout'],
            }
            if self.__settings['time_series_pf'] == 'yes':
                dssDict['yearly'] = self.__settings['solar_csvname'].split('.csv')[0]
            self.__PVSystem[cust+'PV'] = dssDict
        self.__toDSS('PVsystem',self.__PVSystem)

    def __Create_loadshape(self):
        
        files = os.listdir(os.path.join(self.path,'ExtraCSVs'))
        if self.__settings['include_PV']: 
            self.__uniquecusttype.append(self.__settings['solar_csvname'].split('.csv')[0])
            assert self.__settings['solar_csvname'] in files, '{} doesnot exist in "ExtraCSVs" folder'.format(self.__settings['solar_csvname'])
        if self.__settings['time_series_voltage_profile'] == 'yes': 
            self.__uniquecusttype.append(self.__settings['voltage_csv_name'].split('.csv')[0])
            assert self.__settings['voltage_csv_name'] in files, '{} doesnot exist in "ExtraCSVs" folder'.format(self.__settings['voltage_csv_name'])
        self.__Loadshape = {}

        
        for el in self.__uniquecusttype:
            dssDict = {
                'npts' : self.__settings['num_of_data_points'],
                'minterval' : self.__settings['minute-interval'],
                'mult': '(file='+ str(el) + '.csv)',
            }
            assert str(el.lower())+'.csv' in files, '{} doesnot exist in "ExtraCSVs" folder'.format(str(el.lower())+'.csv')
            self.__Loadshape[self.__ModifyName(el)] = dssDict
            shutil.copy(os.path.join(self.path,'ExtraCSVs',str(el.lower())+'.csv'), self.__whichpath)
            
        self.__toDSS('loadshape',self.__Loadshape)
    
    def __CreateCircuit(self):

        print('Writing File - ' + self.__ModifyName(self.__settings['Feeder name']) + '.dss')
        file = open(self.__whichpath + '/' + self.__ModifyName(self.__settings['Feeder name']) + '.dss', 'w')
        file.write('clear\n\n')
        if 'loadshape.dss' in self.__DSSfiles:
            file.write('redirect ' + 'loadshape.dss' + '\n\n')
        file.write('New circuit.' + self.__ModifyName(self.__settings['Feeder name']).lower() + '\n')
        
        if self.__settings['time_series_voltage_profile'] == 'yes' and self.__settings['time_series_pf'] == 'yes':
            file.write('~ basekv={0} basefreq={1} pu={2} phases={3} Z1={4} Z0= {5} bus1={6} yearly={7}\n'.format(self.__settings['sourcebasekv'],self.__settings['sourcebasefreq'],self.__settings['sourcepu'],self.__settings['source_num_of_phase'],self.__settings['sourceposseq_impedance'],self.__settings['sourcezeroseq_impedance'],self.swing,self.__settings['voltage_csv_name'].split('.csv')[0]))
        else:
            file.write('~ basekv={0} basefreq={1} pu={2} phases={3} Z1={4} Z0= {5} bus1={6}\n'.format(self.__settings['sourcebasekv'],self.__settings['sourcebasefreq'],self.__settings['sourcepu'],self.__settings['source_num_of_phase'],self.__settings['sourceposseq_impedance'],self.__settings['sourcezeroseq_impedance'],self.swing))
        for Filename in self.__DSSfiles:
            if Filename != 'loadshape.dss':
                file.write('redirect ' + Filename.lower() + '\n\n')
        file.write('Set voltagebases={}\n\n'.format(self.__voltage_collec))
        file.write('Calcv\n\n')
        file.write('new energymeter.vol ' + 'transformer.'+ self.metername + '\n\n')
        if self.__settings['time_series_pf'] == 'yes':
            file.write('set mode = yearly\n\n')
            file.write('set stepsize = 15m\n\n')
        file.write('BusCoords ' + self.__CoordFileName + '\n\n')
        if self.__settings['time_series_pf'] != 'yes':
            file.write('solve\n\n')
            file.write('plot circuit\n\n')
            file.write('plot profile\n\n')
        file.close()
        
    def __createwiredss(self,wiredata):
        self.wire_info = {}
        for i in range(len(wiredata)):
            dssDict = {
               'diam' : wiredata.Diameter[i],
               'GMRac' : wiredata.GMRAC[i],
               'GMRunits' : wiredata.GMRunits[i],
               'normamps' : wiredata.normamps[i],
               'Rac'   : wiredata.Rac[i],
               'Runits' : wiredata.Runits[i],
               'radunits' : wiredata.Radunits[i],
            }
            self.wire_info[self.__ModifyName(wiredata.ID[i])] = dssDict
        self.__toDSS('wiredata', self.wire_info)
    
    def __createlinecodedss(self,linecode):
        self.linecode_info = {}
        for i in range(len(linecode)):
            dssDict = {
               'nphases' : linecode.num_of_phases[i],
               'r0' : linecode.r0[i],
               'r1' : linecode.r1[i],
               'x0' : linecode.x0[i],
               'x1'   : linecode.x1[i],
               'c0' : linecode.c0[i],
               'c1' : linecode.c1[i],
               'units' : linecode.units[i]
            }
            self.linecode_info[self.__ModifyName(linecode.ID[i])] = dssDict
        self.__toDSS('linecode', self.linecode_info)
    
    def __createlinegeometrydss(self,geometry):
        self.linegeometry_info = {}
        for i in range(len(geometry)):

            reduce = 'no' if geometry.num_of_cond[i] == geometry.num_of_phases[i] else 'yes'
                
            dssDict = {
               'nconds' : geometry.num_of_cond[i],
               'nphases' : geometry.num_of_phases[i],
               'reduce' : reduce,
            }
            for k in range(geometry.num_of_cond[i]):

                if geometry.spacing[i] == 'vertical':
                    x = geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k-1) if geometry.num_of_cond[i]>geometry.num_of_phases[i] else geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k)
                    h = geometry.height_of_top_conductor[i] - k*geometry.conductor_spacing[i] 
                
                if geometry.spacing[i] == 'horizontal':
                    x = geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k-1) if geometry.num_of_cond[i]>geometry.num_of_phases[i] else geometry.conductor_spacing[i]*(geometry.num_of_cond[i]-k)
                    h = geometry.height_of_top_conductor[i]
                
                assert geometry.spacing[i] in ['vertical', 'horizontal'], 'new spacing {} not defined in the program'.format(geometry.spacing[i])
                dssDict['cond'+str(k+1)] = {
                    'cond': k+1, 
                    'wire': self.__ModifyName(geometry.phase_conductor[i]),
                    'x': x,
                    'h': h,
                    'units': geometry.units[i],
                }
            if geometry.num_of_cond[i] > geometry.num_of_phases[i]:
                dssDict['cond'+str(geometry.num_of_cond[i])]['wire'] = self.__ModifyName(geometry.neutral_conductor[i])


            self.linegeometry_info[self.__ModifyName(geometry.ID[i])] = dssDict
        self.__toDSS('linegeometry', self.linegeometry_info)


    def __toDSS(self, ElementType, info_dict):
        if '_' in ElementType:
            ElmType = ElementType.split('_')[1]
            FileName = ElementType.split('_')[0]
        else:
            ElmType = ElementType
            FileName = ElementType
        
        print('Writing FIle -' + FileName + '.dss')
        Path = self.__whichpath
        is_dict = 0
        file = open(Path + '/' + FileName + '.dss', 'w')
        self.__DSSfiles.append(FileName + '.dss')
        for Name, Properties in info_dict.items():
            NewCmd = 'New '+ ElmType + '.' + Name + ' '
            for propName, propValue in Properties.items():
                if isinstance(propValue,dict):
                    file.write(NewCmd.lower()+'\n')
                    is_dict = 1
                    NewCmd = '~ '
                    for key, value in propValue.items():
                         NewCmd += key + '=' + str(value) + ' '
                else:
                    NewCmd += propName + '=' + str(propValue ) + ' '
            if is_dict == 0:
                file.write(NewCmd.lower()+'\n')
            else:
                file.write(NewCmd.lower()+'\n')
            file.write('\n')
        file.close()
    
    def __CreateBusXYFile(self):
        print('Writing File - Bus_Coordinates.csv')
        file = open(self.__whichpath + '/Bus_Coordinates.csv', 'w')
        Nodes = self.__nxGraph.nodes()
        for Node in Nodes:
            nodeAttrs = self.__nxGraph.node[Node]
            if 'x' in nodeAttrs and 'y' in nodeAttrs:
                X = nodeAttrs['x']
                Y = nodeAttrs['y']
                file.write(self.__ModifyName(Node) + ', ' + str(X) + ', ' + str(Y) + '\n')
        file.close()
        self.__CoordFileName = 'Bus_Coordinates.csv'
        return
    
    def __ModifyName(self, Name):
        InvalidChars = [' ', ',', '.']
        for InvChar in InvalidChars:
            if InvChar in Name:
                Name = Name.replace(InvChar,'-')
        Name = Name.lower()
        return Name
    
    def __export_downcust_dict(self):  
        line_cust_down = {key:[] for key in self.Lines.keys()}
        line_coords = {'component_name':[],'x1':[],'y1':[],'x2':[],'y2':[]}
        index,counter = 0,0
        print('Please wait untill "line_cust_dict.p" and "line_coords.csv" files are being exported .....>>>>')
        for node1,node2 in self.__nxGraph.edges():
            edgeData = self.__nxGraph[node1][node2]
            if edgeData['Type'] in ['HT_line','LT_line','HT_cable','LT_cable','Service_line']:
                name  = self.__ModifyName(self.__settings['Feeder name'] + edgeData['Type'] + '_' + str(index))
                assert name in line_cust_down,'{} not present in dss files'.format(name)
                temp_network = copy.deepcopy(self.__nxGraph)
                temp_network.remove_edge(node1,node2)
                Islands = list(nx.connected_component_subgraphs(temp_network))
                cust_down = []
                for i in range(len(Islands)):
                    if Islands[i].has_node(self.ssnode) != True:
                        for n in Islands[i].nodes():
                            if 'loads' in Islands[i].node[n]:
                                cust_down.append(self.__ModifyName(list(Islands[i].node[n]['loads'])[0]))
                line_coords['component_name'].append(name)
                line_coords['x1'].append(self.__nxGraph.node[node1]['x'])
                line_coords['y1'].append(self.__nxGraph.node[node1]['y'])
                line_coords['x2'].append(self.__nxGraph.node[node2]['x'])
                line_coords['y2'].append(self.__nxGraph.node[node2]['y'])               
                line_cust_down[name]  = cust_down
                counter+=1
                if edgeData['Type'] in ['LT_line','LT_cable']:
                    if self.__settings['multi_threephase_for_lt'] == 'yes' and self.__settings['num_of_parallel_three_phase']>1:
                        for i in range(self.__settings['num_of_parallel_three_phase']-1):
                            name = self.__ModifyName(self.__ModifyName(self.__settings['Feeder name'] + edgeData['Type'] + '_' + str(index))+'_'+str(i+1))
                            assert name in line_cust_down,'{} not present in dss files'.format(name) 
                            line_cust_down[name]  = cust_down
                            line_coords['component_name'].append(name)
                            line_coords['x1'].append(self.__nxGraph.node[node1]['x'])
                            line_coords['y1'].append(self.__nxGraph.node[node1]['y'])
                            line_coords['x2'].append(self.__nxGraph.node[node2]['x'])
                            line_coords['y2'].append(self.__nxGraph.node[node2]['y'])  
                            counter +=1
                
                index+=1
                print("\r[%-100s] %d%%" % ('>'*int(counter*100/len(line_cust_down)), int(counter*100/len(line_cust_down))),end='')
        pickle.dump(line_cust_down,open(os.path.join(self.__settings['Project path'],'ExportedPickleforRiskAnalysis','line_cust_down.p'),"wb"))
        df = pd.DataFrame.from_dict(line_coords)
        df.to_csv(os.path.join(self.__settings['Project path'],'ExportedcoordCSVs','line_coords.csv'))
        print('\n line_cust_dict.p and line_coords.csv files exported successfully')

        ## Export for transformer
        transformer_coords = {'component_name':[],'x':[],'y':[]}
        transformer_cust_down = {key:[] for key in self.Transformer.keys()}
        index = 0
        print('Please wait untill "transformer_cust_dict.p" and "transformers_coords.csv" files are being exported .....>>>>')
        for node1,node2 in self.__nxGraph.edges():
            edgeData = self.__nxGraph[node1][node2]
            if edgeData['Type'] in ['DTs','PTs']:
                name  = self.__ModifyName(self.__settings['Feeder name'] + edgeData['Type'] + '_' + str(index))
                if name in transformer_cust_down:
                    temp_network = copy.deepcopy(self.__nxGraph)
                    temp_network.remove_edge(node1,node2)
                    Islands = list(nx.connected_component_subgraphs(temp_network))
                    cust_down = []
                    for i in range(len(Islands)):
                        if Islands[i].has_node(self.ssnode) != True:
                            for n in Islands[i].nodes():
                                if 'loads' in Islands[i].node[n]:
                                    cust_down.append(self.__ModifyName(list(Islands[i].node[n]['loads'])[0]))
                
                transformer_cust_down[name]  = cust_down
                transformer_coords['component_name'].append(name)
                transformer_coords['x'].append((self.__nxGraph.node[node1]['x']+self.__nxGraph.node[node2]['x'])/2)
                transformer_coords['y'].append((self.__nxGraph.node[node1]['y']+self.__nxGraph.node[node2]['y'])/2)
                index+=1
                print("\r[%-100s] %d%%" % ('>'*int(index*100/len(transformer_cust_down)), int(index*100/len(transformer_cust_down))),end='')
        pickle.dump(transformer_cust_down,open(os.path.join(self.__settings['Project path'],'ExportedPickleforRiskAnalysis','transformer_cust_down.p'),"wb"))
        df = pd.DataFrame.from_dict(transformer_coords)
        df.to_csv(os.path.join(self.__settings['Project path'],'ExportedcoordCSVs','transformer_coords.csv'))
        print('\n transformer_cust_dict.p and transformer_coords.csv files exported successfully')

        # Export for buses

        node_cust_dict = {}
        node_coords = {'component_name':[],'x':[],'y':[]}
        counter = 0
        print('Please wait untill "node_cust_dict.p" and "node_coords.p" files are being exported .....>>>>')
        for node in self.__nxGraph.nodes():
            temp_network = copy.deepcopy(self.__nxGraph)
            temp_network.remove_node(node)
            Islands = list(nx.connected_component_subgraphs(temp_network))
            cust_down = []
            no_nodes_list = []
            for i in range(len(Islands)):
                if Islands[i].has_node(self.ssnode) == True:
                    no_nodes_list = Islands[i].nodes()
            
            for N2 in temp_network.nodes():
                if 'loads' in temp_network.node[N2] and N2 not in no_nodes_list:
                    cust_down.append(self.__ModifyName(list(temp_network.node[N2]['loads'])[0]))
            
            node_cust_dict[self.__ModifyName(node)] = cust_down
            node_coords['component_name'].append(self.__ModifyName(node))
            node_coords['x'].append(self.__nxGraph.node[node]['x'])
            node_coords['y'].append(self.__nxGraph.node[node]['y'])
        
            counter+=1
            print("\r[%-100s] %d%%" % ('>'*int(counter*100/len(self.__nxGraph.nodes())), int(counter*100/len(self.__nxGraph.nodes()))),end='')
        pickle.dump(node_cust_dict,open(os.path.join(self.__settings['Project path'],'ExportedPickleforRiskAnalysis','node_cust_down.p'),"wb"))
        df = pd.DataFrame.from_dict(node_coords)
        df.to_csv(os.path.join(self.__settings['Project path'],'ExportedcoordCSVs','node_coords.csv'))
        print('\n node_cust_dict.p and node_coords.csv file exported successfully')
    