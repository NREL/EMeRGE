# External libraries
import dash_html_components as html
import dash_core_components as dcc
import dash_daq as daq
import dash_table
from dash.dependencies import Input, Output, State

# Internal libraries
from dssdashboard.constants import METRIC_TEXTS
from dssdashboard.dash_content import create_paragraph
from dssdashboard.dash_plot import line_plot, timeseries_plot, geo_scatter_map

class CreatePVtab:

    def __init__(self,app, data_object, coord_object, settings,logger, unique_tag):

        self.app = app
        self.data_object = data_object
        self.coord_object = coord_object
        self.settings = settings
        self.logger = logger
        self.unique_tag = unique_tag

        self.content = html.Div([
            self.first_layer(),
            self.second_layer(),
            self.third_layer(),
            self.fourth_layer(),
            self.fifth_layer(),
        ])

        self.logger.info('PV tab initiallized !!!')

    def first_layer(self):

        left_col = html.Div([
                            create_paragraph(METRIC_TEXTS['first_layer']['heading'], 
                                            METRIC_TEXTS['first_layer']['detail']),
                            html.Div([
                                dcc.Graph(
                                    figure=line_plot(self.data_object.violation_dict, \
                                                    ylabel='Risk Metric (%)')
                                    )
                                ])
                            ],className="col")
        
        right_col = html.Div([
                            create_paragraph(METRIC_TEXTS['second_layer']['heading'], 
                                            METRIC_TEXTS['second_layer']['detail']),
                            html.Div([
                                dcc.Graph(
                                    figure=line_plot(self.data_object.eff_dict, \
                                                    ylabel='Efficiency (%)')
                                    )
                                ])
                            ],className="col")

        return html.Div([left_col,right_col],className="row margin-top-20")

    def second_layer(self):

        left_col = html.Div([
                            create_paragraph(METRIC_TEXTS['third_layer']['heading'], 
                                            METRIC_TEXTS['third_layer']['detail']),
                            html.Div([
                                dcc.Graph(
                                    figure=line_plot(self.data_object.lol_dict, \
                                                    ylabel='Loss of Life - DTs (%)')
                                    )
                                ])
                            ],className="col")
        
        right_col = html.Div([
                            create_paragraph(METRIC_TEXTS['fourth_layer']['heading'], 
                                            METRIC_TEXTS['fourth_layer']['detail']),
                            html.Div([
                                dcc.Graph(
                                    figure=line_plot(self.data_object.og_dict, \
                                                    ylabel='Ovegeneration (kWh)')
                                    )
                                ])
                            ],className="col")

        return html.Div([left_col,right_col],className="row margin-top-20")

    def third_layer(self):
        
        return  html.Div([
                    create_paragraph(METRIC_TEXTS['fifth_layer']['heading'], 
                                    METRIC_TEXTS['fifth_layer']['detail']),
                    html.Div([
                        html.Div([
                            html.H6("Select System Level Metric"),
                            dcc.Dropdown(
                                id="Metric", 
                                options=[{'label': key, 'value': key} for key in
                                     self.data_object.system_metrics],
                                value=['SARDI_aggregated'], 
                                multi=True, 
                                style={'color': '#000000'})
                        ],className="col DropDown"),
                        
                        html.Div([
                            html.H6("Select PV Penetration Scenario"),
                            dcc.Dropdown(
                                id="PVScenario", 
                                options=[{'label': key, 'value': key} for key in
                                        self.data_object.pv_scenarios], 
                                value='Base',
                                style={'color': '#000000'})
                        ], className="col H6 DropDown"),
                    ], className="row"),
                    html.Div([
                        dcc.Graph(id="TimeSeriesSystemLevelMetric"+self.unique_tag)
                    ])
                ])

    def fourth_layer(self):

        timestamps =  list(self.data_object.system_timeseries_dict['Base']['TimeStamps'])
        return  html.Div([
                    create_paragraph(METRIC_TEXTS['sixth_layer']['heading'], 
                                METRIC_TEXTS['sixth_layer']['heading']),
                    html.Div([
                        html.Div([
                            html.H6("Select Asset Level Metric"),
                            dcc.Dropdown(
                                id="AssetMetric",
                                options=[{'label': key, 'value': key} \
                                            for key in self.data_object.asset_metrics],
                                value='NVRI', 
                                style={'color': '#000000'})
                                ], className="col DropDown"),
                        html.Div([
                            html.H6("Select PV Penetration Scenario"), \
                            dcc.Dropdown(
                                id="PVScenario2",
                                options=[{'label': key, 'value': key}  \
                                            for key in self.data_object.pv_scenarios], 
                                value='Base',
                                style={'color': '#000000'})
                                ], className="col H6 DropDown"),
                        ], className="row"),
                    html.Div([
                        html.H6("Slide for observing temporal change"), \
                        daq.Slider(
                            id="TimeIndex",
                            min=0,
                            max=len(timestamps),
                            value=3,
                            step=1,
                            marks={str(val): {'label': timestamps[val].strftime('%m-%d')} \
                                for val in range(0, len(timestamps), 6)},
                            size=1100,),
                            ], style={"margin-left": "50px", "margin-right": "10px"}),
                    html.Div([
                        dcc.Graph(id="AssetLevelMetricHeatMap"+self.unique_tag)
                    ], style={"margin-top": "30px"}),
                ])

    def fifth_layer(self):
        return  html.Div([
                create_paragraph(METRIC_TEXTS['seventh_layer']['heading'], 
                            METRIC_TEXTS['seventh_layer']['heading']),
                html.Div([
                    html.Div([
                        dash_table.DataTable(
                            id="interactiveTable"+self.unique_tag,
                            columns=[],
                            data=[],
                            sort_action="native",
                            column_selectable="single",
                            sort_mode="multi",
                            page_action="native",
                            page_current=0,
                            page_size=10,
                            style_header={'backgroundColor': 'rgb(30, 30, 30)', 'fontWeight': 'bold'},
                            style_cell={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white'},)
                    ], className="col DropDown"),
                    html.Div([
                        dcc.Graph(id="AssetLocation"+self.unique_tag)
                    ], className="col")
                ], className="row")
                ])
            
        
    def layout(self):

        return self.content

    def marker_dict(self,data,title):

        size_array = [0 + 40 * (value - min(data)) / (max(data) - min(data)) for value in data]

        return dict(color=data, 
                    showscale=True, \
                    colorscale=[[0, "#21c7ef"], [0.33, "#76f2ff"], [0.66, "#ff6969"], [1, "#ff1717"], ],
                    cmin=min(data), 
                    cmax=max(data), 
                    size=size_array,
                    colorbar=dict(  x=0.85, 
                                    len=0.7, 
                                    title=dict( text=title,
                                                font={"color": "#737a8d", \
                                                      "family": "Open Sans", \
                                                      "size": 16}, 
                                                ),
                                    titleside="top", \
                                    tickmode="array",
                                    tickvals=[min(data), max(data)],
                                    ticktext=["{:,.2f}".format(min(data)), "{:,.2f}".format(max(data)),],
                                    ticks="outside", 
                                    thickness=25,
                                    tickfont={"family": "Open Sans", 
                                              "color": "#737a8d", 
                                              "size": 16},
                                  )
                    )

    def call_backs(self):

        @self.app.callback(Output('TimeSeriesSystemLevelMetric'+self.unique_tag, 'figure'), \
                [Input('PVScenario', 'value'), Input('Metric', 'value')])
        def update_time_series_plot(pv_scen, metrics):
            scenario_data = self.data_object.system_timeseries_dict[pv_scen]
            data_dict = {'TimeStamp': scenario_data['TimeStamps']}
            for metric in metrics:
                data_dict[metric] = scenario_data[metric]
            return timeseries_plot(data_dict, ylabel='Metric in %')
            
        
        @self.app.callback([Output("interactiveTable"+self.unique_tag, "data"), 
                Output("interactiveTable"+self.unique_tag, "columns")],[Input("AssetMetric", "value"),\
                    Input("PVScenario2", "value")])
        def update_table(metric, pv_scen):

            dataframe = self.data_object.asset[pv_scen][metric]
            columns = [{"name": col, "id": col, "selectable": True} for col in ['Component', metric]]
            data_dict = [{'Component': dataframe['component_name'].tolist()[index],
                         metric: dataframe['values'].tolist()[index]} for index in
                        range(len(dataframe))]
            return data_dict, columns

        @self.app.callback([Output("AssetLevelMetricHeatMap"+self.unique_tag, "figure"),
                             Output("AssetLocation"+self.unique_tag, "figure")], [Input("AssetMetric", "value"), \
                                Input("PVScenario2", "value"), Input("TimeIndex", "value")])
        def update_asset_metric(metric, pv_scen, time_index):

            # Extract data for selected PVScenario and Given metric
            data_selected = self.data_object.asset_ts[pv_scen][metric].loc[time_index]

            # Component level aggregated metrics extracted
            asset_data = self.data_object.asset[pv_scen][metric]

            # Coordinates for component
            if metric in ['NVRI']: 
                coordinates = self.coord_object.node_xy_dict
            if metric in ['TLRI', 'TE', 'TLOL', 'TOG']: 
                coordinates = self.coord_object.trans_xy_dict
            if metric in ['LE', 'LLRI']: 
                coordinates = self.coord_object.line_coordinate_dict
            if metric in ['CRI']: 
                coordinates = self.coord_object.cust_xy_dict

            # Extracting Metrics and coordintes
            metric_data = [data_selected[keys] for keys in coordinates.keys()]
            x_coordinate = [values['x'] for keys, values in coordinates.items()]
            y_coordinate = [values['y'] for keys, values in coordinates.items()]

            return geo_scatter_map(self.coord_object.x_lines,
                                    self.coord_object.y_lines,
                                    x_coordinate,
                                    y_coordinate,
                                    self.coord_object.initial_x,
                                    self.coord_object.initial_y,
                                    marker=self.marker_dict(metric_data, metric),
                                    height=800,
                                    zoom=14),\
                   geo_scatter_map(self.coord_object.x_lines, 
                                    self.coord_object.y_lines, 
                                    x_coordinate, 
                                    y_coordinate,
                                    self.coord_object.initial_x, 
                                    self.coord_object.initial_y, 
                                    marker=self.marker_dict(asset_data['values'].tolist(),metric))

        

