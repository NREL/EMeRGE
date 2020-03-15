import dash_html_components as html
from ResultDashboard.Dashboard.DashContent import *
from ResultDashboard.Dashboard.DashPlot import *
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
from datetime import datetime as dt
import dash_table
from ResultDashboard.Dashboard.pyPVConnectionAnalysis import *
import numpy as np

class PVConnectionTab:

    def __init__(self,app, DataObject, DashboardSettings):

        self.app = app
        self.DataObject = DataObject
        self.DashboardSettings = DashboardSettings
        #self.DataObject = DataObject
        self.content = html.Div([
            self.SecondLayer(),
            self.FirstLayer(),
            self.FourthLayer(),
            self.ThirdLayer(),
        ])

    def FirstLayer(self):
        self.Heading_content = "PV Connection Request : Control Panel"
        self.Detail_content = " Before accepting PV connection request, utility might need to perform initial assessment of whether such PV connection might affect the grid in an adverse manner or not." \
                              " This tool is exactly for that. When consumer submits PV connection request utiliy can input the parameter here and will show impact on different distribution metrics which helps utility to " \
                              "accept or reject the request."

        Col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                       html.Div([
                           html.Div([daq.Gauge(id='risk',color="#9B51E0",value=0,label='Increase Violation Risk',max=100,min=-100,showCurrentValue=True)],className="col"),
                           html.Div([daq.Gauge(id='overgeneration',color="#9B51E0", value=0,label='Increase in Overgeneration', max=100, min=-100,showCurrentValue=True )], className="col"),
                           html.Div([daq.Gauge(id='loss',color="#9B51E0", value=0,label='Increase in Energy Loss', max=100, min=-100,showCurrentValue=True )], className="col")
                       ],className="row textwhite")])

        return Col

    def SecondLayer(self):
        self.Heading_content = "Input for New PV Request"
        self.Detail_content = " User should input valid data for all the fields below. Please zoom in on the network shown on the right and " \
                              " hover over the node to see the name of the node where PV connection is requested."

        left_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                             html.Div([html.H5("Enter PV capacity in kW")],className='Paragraph'),
                             html.Div([dcc.Input(id='PVcap',placeholder='Enter a value...',type='number',value='',style={"margin-left":"30px"})],),
                             html.Div([html.H5("Enter node name for connecting PV")],className='Paragraph'),
                             html.Div([dcc.Input(id='loadname',placeholder='Enter a value...',type='text',value='',style={"margin-left":"30px"}) ]),
                             html.Div([html.H5("Enter Phase for new PV (RYB or R or Y or B)")],className='Paragraph'),
                             html.Div([dcc.Input(id='phase',placeholder='Enter a value...',type='text',value='',style={"margin-left":"30px"}) ]),
                             html.Div([daq.BooleanSwitch(id="Request",on=False,color="#9B51E0",label="Switch to process request",style={"font-family": "Times New Roman","margin-top":"20px"})])],className="col-4")
        self.Heading_content = "PV analysis time period "
        self.Detail_content = "Perform 24 hour power flow on the backend and compares the result with base case. "

        middle_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                             html.Div([html.H5("Enter time to begin simulation (HH:MM:SS format)")], className='Paragraph'),
                             html.Div([dcc.Input(id='time',placeholder='Enter a value...', type='text', value='',
                                                 style={"margin-left": "30px"})]),
                             html.Div([html.H5("Pick a day to start simulation")], className='Paragraph'),
                             html.Div([dcc.DatePickerSingle(id="Date",min_date_allowed=dt(2018, 1, 1),max_date_allowed=dt(2018, 12, 31),style={"margin-left": "30px", "height":"20px"})]),
                               html.Div([daq.BooleanSwitch(id="Accept", on=False, color="#9B51E0",
                                                           label="Switch to accept request",
                                                           style={"font-family": "Times New Roman",
                                                                  "margin-top": "20px"})])], className="col-4")


        self.Heading_content = "Network to add PV"
        self.Detail_content = " Zoom in the network and hover over to see the name of node where you want to add PV."
        self.x_coordinate = [values['x'] for keys, values in self.DataObject.CustomerCoordinatesDict.items()]
        self.y_coordinate = [values['y'] for keys, values in self.DataObject.CustomerCoordinatesDict.items()]
        texts = [keys for keys, values in self.DataObject.CustomerCoordinatesDict.items()]
        right_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                              html.Div([dcc.Graph(figure=GeoScatterMap(self.DataObject.x_lines,self.DataObject.y_lines,self.x_coordinate,self.y_coordinate,self.DataObject.initial_x, self.DataObject.initial_y,height=350,hovertext=texts,hoverinfo='text').layout())])],className="col-4")
        return html.Div([left_col,middle_col,right_col],className="row")
    
    def ThirdLayer(self):

        self.Heading_content = "Voltage profile"
        self.Detail_content = " The plot below shows voltage heatmap on top of network \
            for last time stamp of the simulation."
        
        #selx_coordinate = [values['x'] for keys, values in self.DataObject.CustomerCoordinatesDict.items()]
        #y_coordinate = [values['y'] for keys, values in self.DataObject.CustomerCoordinatesDict.items()]
       

        left_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
        html.Div([dcc.Graph(id="voltagediff")]),],className='col')

        self.Heading_content = "Line loading heatmap"
        self.Detail_content = " The plot below shows a line loading heatmap on top of network for last time stamp of the \
            simulation."

        right_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                              html.Div([dcc.Graph(id="linediff")]), ], className='col')

        self.Heading_content = "Transformer loading heatmap"
        self.Detail_content = " The plot below shows a transformer loading heatmap on top of network for last time stamp of the \
                   simulation."

        rightmost_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                              html.Div([dcc.Graph(id="transformerdiff")]), ],
                             className='col')


        return html.Div([left_col,right_col,rightmost_col],className='row')

    def FourthLayer(self):

        self.Heading_content = "Voltage profile (Base)"
        self.Detail_content = " The plot below shows voltage heatmap on top of network \
            for last time stamp of the simulation."

        # selx_coordinate = [values['x'] for keys, values in self.DataObject.CustomerCoordinatesDict.items()]
        # y_coordinate = [values['y'] for keys, values in self.DataObject.CustomerCoordinatesDict.items()]

        left_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                             html.Div([dcc.Graph(id="voltageBase")]), ], className='col')

        self.Heading_content = "Line loading heatmap (Base)"
        self.Detail_content = " The plot below shows a line loading heatmap on top of network for last time stamp of the \
            simulation."

        right_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                              html.Div([dcc.Graph(id="lineBase")]), ], className='col')

        self.Heading_content = "Transformer loading heatmap (Base)"
        self.Detail_content = " The plot below shows a transformer loading heatmap on top of network for last time stamp of the \
                   simulation."

        rightmost_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                                  html.Div([dcc.Graph(id="transformerBase")]), ],
                                 className='col')

        return html.Div([left_col, right_col, rightmost_col], className='row')

    def MarkerDict(self,Data, title):

        SizeArray = [0 + 40 * (value - min(Data)) / (max(Data) - min(Data)) for value in Data]

        return dict(color=Data, showscale=True,
                    colorscale=[[0, "#21c7ef"], [0.33, "#76f2ff"], [0.66, "#ff6969"], [1, "#ff1717"], ],
                    cmin=min(Data), cmax=max(Data), size=SizeArray,
                    colorbar=dict(x=0.85, len=0.7, title=dict(text=title,
                                                              font={"color": "#737a8d", "family": "Open Sans",
                                                                    "size": 16}, ),
                                  titleside="top", tickmode="array",
                                  tickvals=[min(Data), max(Data)],
                                  ticktext=["{:,.2f}".format(min(Data)), "{:,.2f}".format(max(Data)), ],
                                  ticks="outside", thickness=25,
                                  tickfont={"family": "Open Sans", "color": "#737a8d", "size": 16},
                                  )
                    )
    def layout(self):
        return self.content

    def MarkerDict(self,Data, title):

        SizeArray = [0 + 40 * (value - min(Data)) / (max(Data) - min(Data)) for value in Data]

        return dict(color=Data, showscale=True,
                    colorscale=[[0, "#21c7ef"], [0.33, "#76f2ff"], [0.66, "#ff6969"], [1, "#ff1717"], ],
                    cmin=min(Data), cmax=max(Data), size=SizeArray,
                    colorbar=dict(x=0.85, len=0.7, title=dict(text=title,
                                                              font={"color": "#737a8d", "family": "Open Sans",
                                                                    "size": 16}, ),
                                  titleside="top", tickmode="array",
                                  tickvals=[min(Data), max(Data)],
                                  ticktext=["{:,.2f}".format(min(Data)), "{:,.2f}".format(max(Data)), ],
                                  ticks="outside", thickness=25,
                                  tickfont={"family": "Open Sans", "color": "#737a8d", "size": 16},
                                  )
                    )


    def Callbacks(self):

        @self.app.callback([Output('risk','value'),Output('overgeneration','value'),Output('loss','value'),Output('voltagediff','figure'),Output('linediff','figure'),Output('transformerdiff','figure'),
                            Output('voltageBase','figure'),Output('lineBase','figure'),Output('transformerBase','figure')], #
                           [Input('PVcap','value'),Input('loadname','value'),Input('phase','value'),
                            Input('Accept','on'),Input('time','value'),Input('Date','date'),Input('Request','on')])
        def UpdateGauze(Capacity, LoadName,Phase,Accept,Time,Day, Request):

            Basemap = GeoScatterMap(self.DataObject.x_lines, self.DataObject.y_lines,
                                    self.x_coordinate, self.y_coordinate,
                                    self.DataObject.initial_x,
                                    self.DataObject.initial_y, height=350,
                                    marker={'size': 0}).layout()

            if Request:
                Mode = 'Daily'
                PVDict = {'LoadName': LoadName, 'Irradiance': 0.98, 'Capacity': float(Capacity), 'InverterOverSizeFactor': 0.9,
                      'KVAR': 0, 'CutIn': 0.05, 'CutOut': 0.05, 'Profile': 'solarmult', 'Phases': Phase}
                TimeDict = {'Mode': Mode, 'Time': Time, 'Day': Day}
                pvcon = PVConnection(self.DashboardSettings,PVDict,TimeDict, Accept)
                risk,overgeneration, loss= pvcon.ProcessResult()

                voltagediff, linediff, transformerdiff, voltage, line, transformer = pvcon.ProcessForDifferenceinParameters()
                BusCoordinates = self.DataObject.NodeCoordinatesDict
                markerarrayvoltage, x_coordinatevoltage,y_coordinatevoltage  = [],[],[]
                for keys, values in voltagediff.items():
                    x_coordinatevoltage.append(BusCoordinates[keys]['x'])
                    y_coordinatevoltage.append(BusCoordinates[keys]['y'])
                    markerarrayvoltage.append(values)

                markerarrayline, x_coordinateline, y_coordinateline = [], [], []
                for keys, values in linediff.items():
                    x_coordinateline.append(self.DataObject.LineCoordintesDict[keys]['x'])
                    y_coordinateline.append(self.DataObject.LineCoordintesDict[keys]['y'])
                    markerarrayline.append(values)

                markerarraytransformer, x_coordinatetransformer, y_coordinatetransformer = [], [], []
                for keys, values in transformerdiff.items():
                    x_coordinatetransformer.append(self.DataObject.TransformerCoordinatesDict[keys]['x'])
                    y_coordinatetransformer.append(self.DataObject.TransformerCoordinatesDict[keys]['y'])
                    markerarraytransformer.append(values)


                return risk,overgeneration, loss, GeoScatterMap(self.DataObject.x_lines,self.DataObject.y_lines,x_coordinatevoltage,
                                                                y_coordinatevoltage,self.DataObject.initial_x, self.DataObject.initial_y,
                                                                marker=self.MarkerDict(markerarrayvoltage, 'Delta (p.u.)'),height=350).layout(),\
                       GeoScatterMap(self.DataObject.x_lines,self.DataObject.y_lines, x_coordinateline,y_coordinateline,self.DataObject.initial_x,
                                                            self.DataObject.initial_y,marker=self.MarkerDict(markerarrayline, 'Delta (p.u.)'),
                                                            height=350).layout(),\
                       GeoScatterMap(self.DataObject.x_lines, self.DataObject.y_lines,x_coordinatetransformer,
                                                          y_coordinatetransformer,self.DataObject.initial_x, self.DataObject.initial_y,
                                                            marker=self.MarkerDict(markerarraytransformer, 'Delta (p.u.)'),height=350).layout(),\
                       GeoScatterMap(self.DataObject.x_lines,
                                                        self.DataObject.y_lines,x_coordinatevoltage,y_coordinatevoltage,self.DataObject.initial_x, self.DataObject.initial_y,
                                                    marker=self.MarkerDict([values for keys,values in voltage.items()], 'Base (p.u.)'),
                                                        height=350).layout(),\
                       GeoScatterMap(self.DataObject.x_lines,self.DataObject.y_lines, x_coordinateline,y_coordinateline,
                                                    self.DataObject.initial_x, self.DataObject.initial_y,
                                                    marker=self.MarkerDict([values for keys,values in line.items()], 'Base (p.u.)'),height=350).layout(),\
                       GeoScatterMap(self.DataObject.x_lines, self.DataObject.y_lines,
                                                    x_coordinatetransformer,y_coordinatetransformer,self.DataObject.initial_x, self.DataObject.initial_y,marker=self.MarkerDict([values for keys,values in transformer.items()], 'Base (p.u.)'),height=350).layout()
            else:
                return None,None, None,Basemap, Basemap, Basemap,Basemap, Basemap, Basemap