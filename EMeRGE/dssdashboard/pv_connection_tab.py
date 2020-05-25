# Standard libraries
from datetime import datetime as dt

# External libraries
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_daq as daq

# Internal libraries
from dssdashboard.dash_content import create_paragraph
from dssdashboard.constants import PVCONNECTION_TEXTS
from dssdashboard.dash_plot import geo_scatter_map
from dssdashboard.process_pv_connection import PVConnection


class PVconnectionTab:

    def __init__(self,app, coord_object, settings, logger):

        self.app = app
        self.coord_object = coord_object
        self.settings = settings
        self.logger = logger

        self.content = html.Div([
            self.first_layer(),
            self.second_layer(),
            self.third_layer(),
            self.fourth_layer()
        ])
    
    def first_layer(self):

        left_col = html.Div([
                        create_paragraph(PVCONNECTION_TEXTS['first_layer']['first_col']['heading'], \
                                    PVCONNECTION_TEXTS['first_layer']['first_col']['detail']),
                        html.Div([html.H5("Enter PV capacity in kW")],className='Paragraph'),
                        html.Div([dcc.Input(id='PVcap',
                                            placeholder='Enter a value...',
                                            type='number',
                                            value='',
                                            style={"margin-left":"30px"})
                                ],),
                        html.Div([html.H5("Enter node name for connecting PV")],className='Paragraph'),
                        html.Div([dcc.Input(id='loadname',
                                            placeholder='Enter a value...',
                                            type='text',
                                            value='',
                                            style={"margin-left":"30px"}) 
                                ]),
                        html.Div([html.H5("Enter Phase for new PV (RYB or R or Y or B)")],className='Paragraph'),
                        html.Div([dcc.Input(id='phase',
                                            placeholder='Enter a value...',
                                            type='text',
                                            value='',
                                            style={"margin-left":"30px"}) 
                                ]),
                        html.Div([daq.BooleanSwitch(id="Request",
                                                    on=False,
                                                    color="#9B51E0",
                                                    label="Switch to process request",
                                                    style={"font-family": "Times New Roman","margin-top":"20px"})
                                ])
                        ],className="col-4")


        middle_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['first_layer']['second_col']['heading'], \
                                    PVCONNECTION_TEXTS['first_layer']['second_col']['detail']),
                            html.Div([
                                html.H5("Enter time to begin simulation (HH:MM:SS format)")
                                ], className='Paragraph'),
                            html.Div([
                                dcc.Input(  id='time',
                                            placeholder='Enter a value...', 
                                            type='text', 
                                            value='',
                                            style={"margin-left": "30px"})
                                    ]),
                            html.Div([html.H5("Pick a day to start simulation")], className='Paragraph'),
                            html.Div([
                                dcc.DatePickerSingle(id="Date",
                                                    min_date_allowed=dt(2018, 1, 1),
                                                    max_date_allowed=dt(2018, 12, 31),
                                                    style={"margin-left": "30px", "height":"20px"})
                                    ]),
                            html.Div([
                                daq.BooleanSwitch(  id="Accept", 
                                                    on=False, 
                                                    color="#9B51E0",
                                                    label="Switch to accept request",
                                                    style={"font-family": "Times New Roman",
                                                                  "margin-top": "20px"})
                                    ]),
                            html.Div([
                                daq.BooleanSwitch(  id="Delete", 
                                                    on=False, 
                                                    color="#9B51E0",
                                                    label="Switch to delete PV",
                                                    style={"font-family": "Times New Roman",
                                                                  "margin-top": "20px"})
                                    ])
                            ], className="col-4")
        
        self.x_coordinate = [values['x'] for keys, values \
                                    in self.coord_object.cust_xy_dict.items()]
        self.y_coordinate = [values['y'] for keys, values \
                                    in self.coord_object.cust_xy_dict.items()]
        self.texts = [keys for keys, values in self.coord_object.cust_xy_dict.items()]
        right_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['first_layer']['third_col']['heading'], \
                                    PVCONNECTION_TEXTS['first_layer']['third_col']['detail']),
                            html.Div([
                                dcc.Graph(figure=geo_scatter_map( self.coord_object.x_lines,
                                                                self.coord_object.y_lines,
                                                                self.x_coordinate,
                                                                self.y_coordinate,
                                                                self.coord_object.initial_x, 
                                                                self.coord_object.initial_y,
                                                                height=350,
                                                                hovertext=self.texts,
                                                                hoverinfo='text'))
                                    ])
                            ],className="col-4")
        
        return html.Div([left_col,middle_col,right_col],className="row")

    def second_layer(self):

        return  html.Div([create_paragraph(PVCONNECTION_TEXTS['second_layer']['heading'], \
                                    PVCONNECTION_TEXTS['second_layer']['detail']),
                    html.Div([
                        html.Div([daq.Gauge(id='nvri',
                                            color="#9B51E0",
                                            value=0,
                                            label='Increase in NVRI',
                                            max=100,
                                            min=-100,
                                            showCurrentValue=True)
                        ],className="col"),
                        html.Div([daq.Gauge(id='cri',
                                            color="#9B51E0", 
                                            value=0,
                                            label='Increase in CRI', 
                                            max=100, min=-100,
                                            showCurrentValue=True )
                        ], className="col"),
                    ],className="row textwhite")
                ])
    
    def third_layer(self):


        left_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['third_layer']['first_col']['heading'], \
                                    PVCONNECTION_TEXTS['third_layer']['first_col']['detail']),
                             html.Div([dcc.Graph(id="voltageBase")]), ], className='col')

        middle_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['third_layer']['second_col']['heading'], \
                                    PVCONNECTION_TEXTS['third_layer']['second_col']['detail']),
                              html.Div([dcc.Graph(id="lineBase")]), ], className='col')

        right_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['third_layer']['third_col']['heading'], \
                                    PVCONNECTION_TEXTS['third_layer']['third_col']['detail']),
                                  html.Div([dcc.Graph(id="transformerBase")]), ],
                                 className='col')

        return html.Div([left_col, middle_col, right_col], className='row')

    
    def fourth_layer(self):
       

        left_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['fourth_layer']['first_col']['heading'], \
                                    PVCONNECTION_TEXTS['fourth_layer']['first_col']['detail']),
                            html.Div([dcc.Graph(id="voltagediff")]),],className='col')

        middle_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['fourth_layer']['second_col']['heading'], \
                                    PVCONNECTION_TEXTS['fourth_layer']['second_col']['detail']),
                                html.Div([dcc.Graph(id="linediff")]), ], className='col')


        right_col = html.Div([create_paragraph(PVCONNECTION_TEXTS['fourth_layer']['third_col']['heading'], \
                                    PVCONNECTION_TEXTS['fourth_layer']['third_col']['detail']),
                              html.Div([dcc.Graph(id="transformerdiff")]), ],
                             className='col')


        return html.Div([left_col,middle_col,right_col],className='row')

    def marker_dict(self,data, title):

        size_array = [0 + 40 * (value - min(data)) / (max(data) - min(data)) for value in data]

        return dict(color=data, 
                    showscale=True,
                    colorscale=[[0, "#21c7ef"], [0.33, "#76f2ff"], [0.66, "#ff6969"], [1, "#ff1717"], ],
                    cmin=min(data), 
                    cmax=max(data), 
                    size=size_array,
                    colorbar=dict(  x=0.85, 
                                    len=0.7, 
                                    title=dict( text=title,
                                                font={"color": "#737a8d", "family": "Open Sans",
                                                    "size": 16}, ),
                                    titleside="top", 
                                    tickmode="array",
                                    tickvals=[min(data), max(data)],
                                    ticktext=["{:,.2f}".format(min(data)), "{:,.2f}".format(max(data)), ],
                                    ticks="outside", 
                                    thickness=25,
                                    tickfont={"family": "Open Sans", "color": "#737a8d", "size": 16},
                                  )
                    )
    def layout(self):

        return self.content

    def call_backs(self):

        @self.app.callback([Output('nvri','value'),Output('cri','value'), \
                            Output('voltagediff','figure'), Output('linediff','figure'),
                            Output('transformerdiff','figure'), Output('voltageBase','figure'),
                            Output('lineBase','figure'), Output('transformerBase','figure')], \
                           [Input('PVcap','value'),Input('loadname','value'), \
                            Input('phase','value'),Input('Accept','on'), \
                            Input('time','value'),Input('Date','date'), \
                            Input('Request','on'),Input('Delete','on')])
        def update_gauze_and_figure(capacity, load_name,phase,accept,time,day, request,delete):

            basemap = geo_scatter_map(  self.coord_object.x_lines, 
                                        self.coord_object.y_lines,
                                        self.x_coordinate, 
                                        self.y_coordinate,
                                        self.coord_object.initial_x,
                                        self.coord_object.initial_y, 
                                        height=350,
                                        marker={'size': 0})
            
            mode = 'Daily'
            if request:
                pv_dict = { 'LoadName': load_name, 
                            'Irradiance': 0.98, 
                            'Capacity': float(capacity), 
                            'InverterOverSizeFactor': 0.9,
                            'KVAR': 0, 
                            'CutIn': 0.05, 
                            'CutOut': 0.05, 
                            'Profile': 'solarmult', 
                            'Phases': phase}

                time = day if ':' in day else day + ' ' + time

                time_dict = {'Mode': mode, 'Time': time}
                file_dict = {'Accept':False,'Delete':False}
                pvcon_instance = PVConnection(self.settings,self.logger,pv_dict,time_dict,file_dict)
                pvcon_instance.run_powerflow()
                result_diff_dict = pvcon_instance.process_results()
                metric_diff = pvcon_instance.process_metrics()

                marker_dict,coordinate_dict = {},{}

                coord_dict = {'voltages':self.coord_object.node_xy_dict,
                                'lineloading':self.coord_object.line_coordinate_dict,
                                'transloading':self.coord_object.trans_xy_dict}

                for param, subdict in result_diff_dict.items():
                    
                    coordinate_dict[param] = {
                        'x' : [coord_dict[param][keys]['x'] \
                                    for keys in subdict['max_diff'].keys()],
                        'y' : [coord_dict[param][keys]['y'] \
                                    for keys in subdict['max_diff'].keys()]
                    }

                    marker_dict[param] = list(subdict['max_diff'].values())

                return  metric_diff['NVRI'], \
                        metric_diff['CRI'], \
                        geo_scatter_map(self.coord_object.x_lines,
                                        self.coord_object.y_lines,
                                        coordinate_dict['voltages']['x'],
                                        coordinate_dict['voltages']['y'],
                                        self.coord_object.initial_x, 
                                        self.coord_object.initial_y,
                                        marker=self.marker_dict(marker_dict['voltages'], 'Delta (p.u.)'),
                                        height=350),\
                       geo_scatter_map( self.coord_object.x_lines,
                                        self.coord_object.y_lines, 
                                        coordinate_dict['lineloading']['x'],
                                        coordinate_dict['lineloading']['y'],
                                        self.coord_object.initial_x,
                                        self.coord_object.initial_y,
                                        marker=self.marker_dict(marker_dict['lineloading'], 'Delta (p.u.)'),
                                        height=350),\
                       geo_scatter_map( self.coord_object.x_lines, 
                                        self.coord_object.y_lines,
                                        coordinate_dict['transloading']['x'],
                                        coordinate_dict['transloading']['y'],
                                        self.coord_object.initial_x, 
                                        self.coord_object.initial_y,
                                        marker=self.marker_dict(marker_dict['transloading'], 'Delta (p.u.)'),
                                        height=350),\
                       geo_scatter_map( self.coord_object.x_lines,
                                        self.coord_object.y_lines,
                                        coordinate_dict['voltages']['x'],
                                        coordinate_dict['voltages']['y'],
                                        self.coord_object.initial_x, 
                                        self.coord_object.initial_y,
                                        marker=self.marker_dict([values for keys,values \
                                                in result_diff_dict['voltages']['Base'].items()], 'Base (p.u.)'),
                                        height=350),\
                       geo_scatter_map( self.coord_object.x_lines,
                                        self.coord_object.y_lines, 
                                        coordinate_dict['lineloading']['x'],
                                        coordinate_dict['lineloading']['y'],
                                        self.coord_object.initial_x, 
                                        self.coord_object.initial_y,
                                        marker=self.marker_dict([values for keys,values \
                                                in result_diff_dict['lineloading']['Base'].items()], 'Base (p.u.)'),
                                        height=350),\
                       geo_scatter_map( self.coord_object.x_lines, 
                                        self.coord_object.y_lines,
                                        coordinate_dict['transloading']['x'],
                                        coordinate_dict['transloading']['y'],
                                        self.coord_object.initial_x, 
                                        self.coord_object.initial_y,
                                        marker=self.marker_dict([values for keys,values \
                                                in result_diff_dict['transloading']['Base'].items()], 'Base (p.u.)'),
                                        height=350)
            else:

                if accept == True or delete == True:
                    pv_dict = { 'LoadName': load_name, 
                            'Irradiance': 0.98, 
                            'Capacity': float(capacity), 
                            'InverterOverSizeFactor': 0.9,
                            'KVAR': 0, 
                            'CutIn': 0.05, 
                            'CutOut': 0.05, 
                            'Profile': 'solarmult', 
                            'Phases': phase}

                    time = day if ':' in day else day + ' ' + time
                    time_dict = {'Mode': mode, 'Time': time}
                    file_dict = {'Accept':accept,'Delete':delete}
                    pvcon_instance = PVConnection(self.settings,self.logger,pv_dict,time_dict,file_dict)
                
                return None,None,basemap, basemap, basemap,basemap, basemap, basemap
