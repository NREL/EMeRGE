"""
Created on Wed Sep 11 1:43:57 2019
@author: kduwadi
"""

# Standard libraries
import pathlib, os
import copy
import random
import math

# External libraries
import numpy as np 
import pandas as pd
import networkx as nx

class Reader:

    code_name = {
        'consumer_ht.csv' : {'code': 'N', 'type': 'Consumer_HT'},
        'consumer_lt.csv' : {'code': 'N', 'type': 'Consumer_LT'},
        'distribution_transformer.csv' : {'code': 'N', 'type': 'DTs'},
        'ht_cable_attributes.csv' : {'code': 'L', 'type': 'HT_cable', 'feature': 'Attribute data'},
        'ht_cable_nodes.csv' : {'code': 'L', 'type': 'HT_cable', 'feature': 'Coordinates'},
        'ht_line_attributes.csv' : {'code': 'L', 'type': 'HT_line', 'feature': 'Attribute data'},
        'ht_line_nodes.csv' : {'code': 'L', 'type': 'HT_line', 'feature': 'Coordinates'},
        'ht_pole.csv' : {'code': 'N', 'type': 'HTpole'},
        'lt_cable_attributes.csv' : {'code': 'L', 'type': 'LT_cable', 'feature': 'Attribute data'},
        'lt_cable_nodes.csv' : {'code': 'L', 'type': 'LT_cable', 'feature': 'Coordinates'},
        'lt_line_attributes.csv' : {'code': 'L', 'type': 'LT_line', 'feature': 'Attribute data'},
        'lt_line_nodes.csv' : {'code': 'L', 'type': 'LT_line', 'feature': 'Coordinates'},
        'lt_pole.csv' : {'code': 'N', 'type': 'LTpole'},
        'power_transformer.csv' : {'code': 'N', 'type': 'PTs'},
    }

    def __init__(self,settings,logger):
        
        self.settings = settings
        self.logger = logger
        self.path = os.path.join(self.settings["project_path"],self.settings["feeder_name"])
        self.filelists = os.listdir(self.path)
        self.feedername = self.settings["feeder_name"]
        self.create_file_dictionary()
        

        self.logger.info(f'Developing network for feeder {self.feedername} >>>>')

        self.line_data = {}
        for element, file_dict in self.line_files.items():
            coordinate_data = pd.read_csv(os.path.join(self.path, file_dict['Coordinates']),index_col=None)
            attribute_data = pd.read_csv(os.path.join(self.path, file_dict['Attribute data']),index_col=None)
            self.line_data[element] = {'CD' : coordinate_data, 'ATD' : attribute_data}
        
        self.node_data = {}
        for element, file_path in self.node_files.items():
            node_data = pd.read_csv(os.path.join(self.path,file_path),index_col=None)
            self.node_data[element] = node_data
        
        self.nxgraph = nx.Graph()

        # This portion of the code generates HT network amd checks for any islands or loops, 
        # and fixes islands on its own if present

        if 'HT_line' in self.line_files:
            self.logger.info('Creating HT_edges')
            self.add_edge('HT_line', 'HT')
        if 'HT_cable' in self.line_files:
            self.logger.info('Creating HT_Cables')
            self.add_edge('HT_cable', 'HT')
        if 'HT_line' in self.line_files or 'HT_cable' in self.line_files:
            self.get_graphmetrics()
        else:
            self.logger.info("The network you are trying to build does not seem to" \
                        "have high tension network. Make sure this is correct. If its" 
                        "wrong please abort the program and make sure you have csvs with correct names...!!!")

        # This portion of the code builds LT network and adds transformer to it 
        
        if 'LT_line' in self.line_files:
            self.logger.info('Creating LT_edges')
            self.add_edge('LT_line', 'LT')
        if 'LT_cable' in self.line_files:
            self.logger.info('Creating LT_Cables')
            self.add_edge('LT_cable', 'LT')
        if 'DTs' in self.node_files:
            if 'HT_line' in self.line_files or 'HT_cable' in self.line_files:
                self.add_distribution_transformers()
            else:
                self.logger.info("Distribution transformers are used to connect HT and LT network ," \
                        "without HT network program can not utillize distribution_transformer.csv:" \
                        "if this is substation transformer please make sure you include this in power_transformer.csv")
        if 'LT_line' in self.line_files or 'LT_cable' in self.line_files:
            self.get_graphmetrics()
        else:
            self.logger.info("The network you are trying to build does not seem to have low tension network." \
                            "Make sure this is correct. If its wrong please abort the program and" 
                            "make sure you have csvs with correct names...!!!")
            if 'HT_line' not in self.line_files and 'HT_cable' not in self.line_files:
                assert False, "There is no network build upto this point: make sure files \
                are named correctly or check if folder is empty"


        # This portion of the code adds power transformer to the network
        if 'PTs' in self.node_files:
            self.add_power_transformers()
        else:
            self.logger.info("Caution: This network does not seem to have power transformers !!!")


        # This portion of the network adds consumers to the network

        if 'Consumer_LT' in self.node_files:
            self.logger.info('Adding LT customers to network')
            self.add_loads(self.node_data['Consumer_LT'],'LT')
        if 'Consumer_HT' in self.node_files:
            self.logger.info('Adding HT customers to network')
            self.add_loads(self.node_data['Consumer_HT'],'HT')
        
        self.get_graphmetrics()
        self.logger.info(f'Successfully build the {self.feedername} Feeder !!!!!!')

        return
    
    def create_file_dictionary(self):
        self.line_files = {}
        self.node_files = {}
        for i in range(len(self.filelists)):
            this_dict = self.code_name[self.filelists[i]]
            if this_dict['code'] == 'N':
                self.node_files[this_dict['type']] = self.filelists[i]
            else:
                if this_dict['type'] not in self.line_files:
                    self.line_files[this_dict['type']] = {}
                    self.line_files[this_dict['type']][this_dict['feature']] = self.filelists[i]
                else:
                    self.line_files[this_dict['type']][this_dict['feature']] = self.filelists[i]
        return

    
    def add_edge(self, tag, acronym):

        c_data = self.line_data[tag]['CD']
        a_data = self.line_data[tag]['ATD']

        D = len(a_data)
            
        for i in range(D):
            row_att_data = a_data.loc[i]
            shape_id = row_att_data['shapeid']
            elm_coord_data = c_data[c_data['shapeid'] == shape_id]
            elm_coord_data.index = range(len(elm_coord_data))
            x1 = elm_coord_data['x'][0]
            x2 = elm_coord_data['x'][len(elm_coord_data)-1]
            y1 = elm_coord_data['y'][0]
            y2 = elm_coord_data['y'][len(elm_coord_data)-1]
        
            attributes = {
                'Type'       : tag,      
                'Length'     : row_att_data["length"],
                'Phase_con'      : row_att_data["phase"],
                'Cable size phase'   : row_att_data["csize"],
                'num_of_cond'  : row_att_data["num_of_cond"],
                'Cable type phase'   : row_att_data["cname"],
                'spacing' : row_att_data['spacing'],
                'units' : row_att_data['units']
                }
            if 'nname' in row_att_data:
                attributes['Cable type neutral'] = row_att_data["nname"]
                attributes['Cable size neutral'] = row_att_data["nsize"]

            self.nxgraph.add_edge('{}_{}_{}'.format(x1,y1,acronym), '{}_{}_{}'.format(x2,y2,acronym), **attributes)
            self.nxgraph.node['{}_{}_{}'.format(x1,y1,acronym)]['x'] = x1
            self.nxgraph.node['{}_{}_{}'.format(x1,y1,acronym)]['y'] = y1
            self.nxgraph.node['{}_{}_{}'.format(x1,y1,acronym)]['Type'] = acronym + 'node'
            self.nxgraph.node['{}_{}_{}'.format(x2,y2,acronym)]['x'] = x2
            self.nxgraph.node['{}_{}_{}'.format(x2,y2,acronym)]['y'] = y2
            self.nxgraph.node['{}_{}_{}'.format(x2,y2,acronym)]['Type'] = acronym + 'node'
        return
        

    def get_graphmetrics(self):

        self.islands = list(nx.connected_component_subgraphs(self.nxgraph))
        self.num_of_islands = len(self.islands)
        self.loops = nx.cycle_basis(self.nxgraph)
        if self.num_of_islands >1:
            self.logger.info(f"Caution: the network upto this point has {self.num_of_islands} islands: running" \
                            "inbuilt algorithm to fix island issue")
            self.fix_network_islands()
            assert len(list(nx.connected_component_subgraphs(self.nxgraph)))==1, \
                'Especial error -- > The inbuilt algorithm is not able to successully fix issue of \
                islands: Please consult with NREL team ro fix this !!!'

        assert len(self.loops)==0, "Especial error -- > The program does not have inbuilt \
            algoritm to fix loops present within network for now: Please consult with NREL team to fix this !!!"
    
    
    def fix_network_islands(self):

        self.islands = list(nx.connected_component_subgraphs(self.nxgraph))

        for _ in range(len(self.islands)-1):
            d = 99999999
            for node1 in self.islands[0].nodes():
                x0 = self.islands[0].node[node1]['x']
                y0 = self.islands[0].node[node1]['y']
                for k in range(len(self.islands)):
                    if k != 0:
                        for node2 in self.islands[k].nodes():
                            x1 =  self.islands[k].node[node2]['x']
                            y1 =  self.islands[k].node[node2]['y']
                            if np.sqrt((x0-x1)**2+(y0-y1)**2) < d:
                                if self.nxgraph.nodes[node2]["Type"] == self.nxgraph.nodes[node1]["Type"]:
                                    d = np.sqrt((x0-x1)**2+(y0-y1)**2)
                                    n1 = node1
                                    n2 = node2
            self.nxgraph = nx.contracted_nodes(self.nxgraph,n1,n2)
            self.islands = list(nx.connected_component_subgraphs(self.nxgraph))
    
    
    def add_distribution_transformers(self):

        self.logger.info("Adding distribution transformers")
        type_data = self.node_data['DTs']
            
        for i in range(len(type_data)):
            trans_data = type_data.loc[i]
            elm_dict  = trans_data.to_dict()
            elm_dict['Type'] =  'DTs'
                    
            x0,y0 = trans_data['x'],trans_data['y']
            dist_from_ht_node,dist_from_lt_node,nearest_ht_node,nearest_lt_node = 99999999,99999999,None,None
                   
            for node in self.nxgraph.nodes():
                x1 = self.nxgraph.node[node]['x']
                y1 = self.nxgraph.node[node]['y']
                        
                if self.nxgraph.node[node]['Type'] == 'HTnode':
                    if np.sqrt((x1-x0)**2+(y1-y0)**2) < dist_from_ht_node:
                        dist_from_ht_node = np.sqrt((x1-x0)**2+(y1-y0)**2)
                        nearest_ht_node = node
                        
                elif self.nxgraph.node[node]['Type'] == 'LTnode':
                    if np.sqrt((x1-x0)**2+(y1-y0)**2) < dist_from_lt_node:
                        dist_from_lt_node = np.sqrt((x1-x0)**2+(y1-y0)**2)
                        nearest_lt_node = node               
            self.nxgraph.add_edge(nearest_ht_node, nearest_lt_node, **elm_dict)
        return


    def add_power_transformers(self):
        
        self.logger.info("Adding power transformers")
        type_data = self.node_data['PTs']
        trans_data = type_data.loc[0]
        elm_dict  = trans_data.to_dict()
        elm_dict['Type'] =  'PTs'
        x0,y0,dist_from_ht,node_of_interest  = self.node_data['PTs'].x[0],self.node_data['PTs'].y[0],9999999,None
        for node in self.nxgraph.nodes():
            if self.nxgraph.node[node]['Type'] == 'HTnode':
                x1 = self.nxgraph.node[node]['x']
                y1 = self.nxgraph.node[node]['y']

                if np.sqrt((x0-x1)**2+(y0-y1)**2) < dist_from_ht:
                    dist_from_consumer_ht =  np.sqrt((x0-x1)**2+(y0-y1)**2)
                    node_of_interest = node
                                   
        self.nxgraph.add_edge('{}_{}_EHT'.format(x0,y0),node_of_interest, **elm_dict)
        self.nxgraph.node['{}_{}_EHT'.format(x0,y0)]['x'] = x0
        self.nxgraph.node['{}_{}_EHT'.format(x0,y0)]['y'] = y0
        self.nxgraph.node['{}_{}_EHT'.format(x0,y0)]['Type'] = 'EHTnode'
                

    
    def add_loads(self, con_data, tag):

        # Find nearest node for connecting consumer
       
        for i in range(len(con_data)):
            x0,y0 = con_data.x[i],con_data.y[i]
            dist_from_consumer_lt,node_of_interest = 9999999,None
            for node in self.nxgraph.nodes():
                if self.nxgraph.node[node]['Type'] == tag+'node':
                    x1 = self.nxgraph.node[node]['x']
                    y1 = self.nxgraph.node[node]['y']

                    if np.sqrt((x0-x1)**2+(y0-y1)**2) < dist_from_consumer_lt:
                        dist_from_consumer_lt =  np.sqrt((x0-x1)**2+(y0-y1)**2)
                        node_of_interest = node
            
            #  do random phase allocation to single phase LT consumers if necessary

            if con_data.phase[i] != self.settings['three_phase'] and \
                            self.settings['random_phase_allocation'] == 'yes' and tag=="LT":
                phase = random.choice(self.settings["single_phase"])
            else:
                phase = con_data.phase[i]
            
            # adding property to conductors for connecting consumer to nearest node
            
            line_type = 'Service_line' if tag=='LT' else tag+'_line'
            phase_conductor_type = self.settings['servicewire_phase_conductor_type'] if tag=='LT' \
                        else self.settings['phase_conductor_type_ht_consumer']
            phase_conductor_size = self.settings['servicewire_phase_conductor_size'] if tag=='LT' \
                        else self.settings['phase_conductor_size_ht_consumer']

            if phase != "RYB":
                num_of_cond = self.settings["service_wire_num_of_cond"]["single_phase"]
            else:
                num_of_cond = self.settings["service_wire_num_of_cond"]["three_phase"] if tag=="LT" \
                        else self.settings["ht_consumer_conductor_num_of_cond"]["three_phase"]

            spacing = self.settings['service_wire_spacing'] if tag=="LT" \
                        else self.settings['ht_consumer_conductor_spacing']
            attributes = {
                'Type'               : line_type, 
                'Phase_con'          : phase,
                'Length'             : dist_from_consumer_lt,
                'num_of_cond'        : num_of_cond,
                'Cable size phase'   : phase_conductor_size,
                'Cable type phase'   : phase_conductor_type,
                'spacing'            : spacing,
                'units'              : self.settings['units_for_coordinate']
                }
            # add edge for connecting consumers

            self.nxgraph.add_edge('{}_{}_{}'.format(x0,y0,tag),node_of_interest, **attributes)
            self.nxgraph.node['{}_{}_{}'.format(x0,y0,tag)]['x'] = x0
            self.nxgraph.node['{}_{}_{}'.format(x0,y0,tag)]['y'] = y0
            self.nxgraph.node['{}_{}_{}'.format(x0,y0,tag)]['Type'] = 'STnode' if tag=="LT" else "HTnode"

            
            #mult_fact = {'Residential': 5937.831,'Commercial':6168.84,'Industrial':6206.385,'Agricultural':6102.5}

            node_data = self.nxgraph.node['{}_{}_{}'.format(x0,y0,tag)]
            if 'loads' not in node_data:
                node_data['loads']  ={}
            node_data['loads'][con_data.ID[i]]= {
                'kw'  : con_data.kw[i],
                'pf'    : con_data.pf[i],
                'phase' : phase,
                'kv' : con_data.kv[i],
                'tec' : con_data.tec[i],
                'con_type': con_data.cust_type[i],
                'load_type': con_data.load_type[i]
            }
    

# ------------------------------------------------------------------------------------------------------------------------------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

  