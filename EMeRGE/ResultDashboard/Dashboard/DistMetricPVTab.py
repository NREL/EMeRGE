import dash_html_components as html
from ResultDashboard.Dashboard.DashContent import *
from ResultDashboard.Dashboard.DashPlot import *
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
import dash_table

class DistMetricPVTab:

    def __init__(self,app, DataObject ):

        self.app = app
        self.DataObject = DataObject
        self.content = html.Div([
            self.FirstLayer(),
            self.SecondLayer(),
            self.ThirdLayer(),
            self.FourthLayer(),
            self.FifthLayer(),
        ])

    def FirstLayer(self):
        self.Heading_content = "System Level Risk Metrics"
        self.Detail_content = "Percentage time average customer would experience violations are defined as risk metrics. Violations are categorized into three types: Voltage violation (any voltage magnitude above 1.1 pu and below 0.9 pu)" \
                              " , line violation (loading aboove 100%) and transformer violation (above 100%). SARDI_voltage, SARDI_line, SARDI_transformer represent System Average Risk Duration Index for voltage, line and transformer violation" \
                              " respectievely. SARDI_aggregated represents System Average Risk Duration Index for all violations. Knowing how PV deployement would alter these risk metrics can better inform PV deployement decisions. Base case" \
                              " means no PV. PV scenarios is defined by two components. For e.g. 10%-100% PV scenario means that 10% of total customers (chosen uniformly randomly) have installed PV with a capcity to meet 100% of their annual energy need " \
                              " when they do not have PV in their system."
        left_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),html.Div([dcc.Graph(figure=LinePlot(self.DataObject.ViolationDict,ylabel='Risk Metric (%)').layout())])],className="col")
        self.Heading_content = "Percentage Energy Loss"
        self.Detail_content = "Percentage energy Loss is an indicator of efficiency. Loss in the energy is a loss in economic reveune and also increases loss of life of an equipment (such as conductors and transformers)." \
                              " Along with risk metrics we also need to see how PV deployment affects percentage energy loss. Higher deployement of PV would increase loading in the distribution network thus increasing loss in the system. " \
                              "SE_line, SE_transformer and SE represent system energy loss for line elements (including both conductors and cables), system energy loss for transformers and overall system energy loss. Accuracy of these results depend on accuracy of" \
                              "parameters of component such as resistance, reactance, capacitance, percentage loss during full load and no load of transformer etc. Furthermore, how accurate load profiles are also has an impact. Field measurements could certainly help " \
                              "validating these results."

        right_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),html.Div([dcc.Graph(figure=LinePlot(self.DataObject.Efficiency,ylabel='Energy Loss (%)').layout())])],className="col")

        return html.Div([left_col,right_col],className="row margin-top-20")
    def SecondLayer(self):
        self.Heading_content = "Percentage Loss of Life of Transformer"
        self.Detail_content = "Transformer loss of life is a function of hot-spot temperature inside transformer element. Hot spot temperature further depends on loading pattern which certainly would be affected by PV deployment." \
                              " IEEE C57.92-1981 provides detail description on how to compute loss of life from loading pattern. Here we have assumed life of transformer is determined by deterioration of insulating material because of" \
                              " temperature. The numbers are reliable only if the loadings are normal (meaning not severly high for long period of time). This may not be highly accurate now however provides relative understanding pattern in loss of life " \
                              "because of PV deployement providing more support to PV deployement decision."
        left_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),html.Div([dcc.Graph(figure=LinePlot(self.DataObject.Lossoflife,ylabel='Loss of Life - DTs (%)').layout())])],className="col")
        self.Heading_content = "Percentage Overgeneration by PV"
        self.Detail_content = "Higher deployment of PV can cause reverse power flow in the system which can accumulate at the substation level. If there is a limit on reverse power flow because of storage constraints or market constraints or any other" \
                              " constraints deploying PV above certain percentage of overgeneration might be infesabile to utility. This metric further complements the PV deployement decesion by providing more insight on" \
                              " PV overgeneration. For now we have not included storage in the system. Furthermore, more advanced protection scheme might be necessary to allow reverse power flow in the system."
        right_col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),html.Div([dcc.Graph(figure=LinePlot(self.DataObject.overgeneration,ylabel='PV Overgeneration (%)').layout())])],className="col")

        return html.Div([left_col,right_col],className="row margin-top-20")

    def ThirdLayer(self):
        self.Heading_content = "Time Series System Level Metrics: Understading daily variation of system level risk metrics"
        self.Detail_content = "Now let's take a look at above metrics in time-series mode. How would above metrics vary in time at different PV scenarios would help us identify day when they are highly impacted. You can select PV scenarios and observe metric variation in the graph." \
                              "Note you can multi-select parameters to observe. Values are aggregated for day."
        col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                        html.Div([
                            html.Div([html.H6("Select System Level Metric"),
                                      dcc.Dropdown(id="Metric", options=[{'label': key, 'value': key} for key in
                                                                         self.DataObject.SystemMetrics],
                                                   value=['SARDI_aggregated'], multi=True, style={'color': '#000000'})],
                                     className="col DropDown"),
                            html.Div([html.H6("Select PV Penetration Scenario"),
                                      dcc.Dropdown(id="PVScenario", options=[{'label': key, 'value': key} for key in
                                                                             self.DataObject.Scenarios], value='Base',
                                                   style={'color': '#000000'})], className="col H6 DropDown"),
                        ], className="row"),
                        html.Div([dcc.Graph(id="TimeSeriesSystemLevelMetric")])])
        return col


    def FourthLayer(self):
        TimeStamps = list(self.DataObject.SystemLevelMetricsTimeSeries['Base']['TimeStamp'])
        self.Heading_content = "Time Series Asset Level Metric: Scatter plot on top of network map"
        self.Detail_content = "Now that we know what the system level distribution metric look like, it is also important to know which asset are at vulnerable state or which asset" \
                              " is actually causing problem. The Scatter plot on top of network allows utility which components are vulnerable and where they are located and at what time. User can use dropdown menu to select different" \
                              " PV scenarios."

        col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                        html.Div([html.Div([html.H6("Select Asset Level Metric"),
                                   dcc.Dropdown(id="AssetMetric",
                                                options=[{'label': key, 'value': key} for key in self.DataObject.AssetLevelMetrics],
                                                value='NVRI', style={'color': '#000000'})], className="col DropDown"),
                         html.Div([html.H6("Select PV Penetration Scenario"),
                                   dcc.Dropdown(id="PVScenario2",
                                   options=[{'label': key, 'value': key} for key in self.DataObject.Scenarios], value='Base',
                                   style={'color': '#000000'})], className="col H6 DropDown"),], className="row"),

                        html.Div([html.H6("Slide for observing temporal change"),
                                  daq.Slider(id="TimeIndex",min=0,max=len(TimeStamps),value=3,step=1,marks={str(val): {'label': TimeStamps[val].strftime('%m-%d')} for val in range(0, len(TimeStamps), 6)},size=1100,),
                                  ], style={"margin-left": "50px", "margin-right": "10px"}),
                        html.Div([dcc.Graph(id="AssetLevelMetricHeatMap")], style={"margin-top": "30px"}),])
        return col

    def FifthLayer(self):

        self.Heading_content = "Asset Level Metric: Table and Aggregated Map"
        self.Detail_content = " The aggreagted metric for an asset is listed in table on the right and shown in the form of scatter heatmap on the left. Size and color both help to identify vulnerable component." \
                              " The components are selected based on the metric you selected to observe in time series asset level metric."

        col = html.Div([Paragraph(self.Heading_content, self.Detail_content).layout(),
                        html.Div([dash_table.DataTable(id="interactiveTable",columns=[],data=[],sort_action="native",column_selectable="single",
                                                       sort_mode="multi",page_action="native",page_current=0,page_size=10,style_header={'backgroundColor': 'rgb(30, 30, 30)', 'fontWeight': 'bold'},
                                                       style_cell={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},)], className="col DropDown"),
                        html.Div([dcc.Graph(id="AssetLocation")], className="col")], className="row")
        return col

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
        @self.app.callback(Output('TimeSeriesSystemLevelMetric', 'figure'), [Input('PVScenario', 'value'), Input('Metric', 'value')])
        def UpdateTimeSeriesPlot(PVscenario, Metric):
            ScenarioData = self.DataObject.SystemLevelMetricsTimeSeries[PVscenario]
            DataDict = {'TimeStamp': ScenarioData['TimeStamp']}
            for metric in Metric:
                DataDict[metric] = ScenarioData[metric]
            return TimeSeriesLinePlot(DataDict, ylabel='Metric in %').layout()


        @self.app.callback([Output("interactiveTable", "data"), Output("interactiveTable", "columns")],
                      [Input("AssetMetric", "value"), Input("PVScenario2", "value")])
        def update_table(Metric, PVScenario):

            DataFrameSelected = self.DataObject.AssetMetricsAggregated[PVScenario][Metric]
            columns = [{"name": col, "id": col, "selectable": True} for col in ['Component', Metric]]
            DataDict = [{'Component': DataFrameSelected['Metrics'].tolist()[index],
                         Metric: DataFrameSelected['Values'].tolist()[index]} for index in
                        range(len(DataFrameSelected))]
            return DataDict, columns

        @self.app.callback([Output("AssetLevelMetricHeatMap", "figure"), Output("AssetLocation", "figure")],
                      [Input("AssetMetric", "value"), Input("PVScenario2", "value"), Input("TimeIndex", "value")])
        def UpdateAssetMetricOverNetwork(Metric, PVScenario, TimeIndex):

            # Extract data for selected PVScenario and Given metric
            DataSelected = self.DataObject.AssetMetricsTimeSeries[PVScenario][Metric].loc[TimeIndex]

            # Coordinates to plot PV points
            PVcoordinates = self.DataObject.PVcoordinates[PVScenario]

            # Component level aggregated metrics extracted
            AggregatedAssetData = self.DataObject.AssetMetricsAggregated[PVScenario][Metric]

            # Coordinates for component
            if Metric in ['NVRI']: ComponentCoordinates = self.DataObject.NodeCoordinatesDict
            if Metric in ['TVRI', 'TE', 'TLOF', 'TOG']: ComponentCoordinates = self.DataObject.TransformerCoordinatesDict
            if Metric in ['LE', 'LVRI']: ComponentCoordinates = self.DataObject.LineCoordintesDict
            if Metric in ['CRI']: ComponentCoordinates = self.DataObject.CustomerCoordinatesDict

            # Extracting Metrics and coordintes
            MetricArray = [DataSelected[keys] for keys in ComponentCoordinates.keys()]
            x_coordinate = [values['x'] for keys, values in ComponentCoordinates.items()]
            y_coordinate = [values['y'] for keys, values in ComponentCoordinates.items()]


            return GeoScatterMap(self.DataObject.x_lines,self.DataObject.y_lines,x_coordinate,y_coordinate,self.DataObject.initial_x,self.DataObject.initial_y,marker=self.MarkerDict(MetricArray, Metric),height=800,zoom=14).layout(),\
                   GeoScatterMap(self.DataObject.x_lines, self.DataObject.y_lines, x_coordinate, y_coordinate,
                          self.DataObject.initial_x, self.DataObject.initial_y, marker=self.MarkerDict(AggregatedAssetData['Values'].tolist(),Metric)).layout()



