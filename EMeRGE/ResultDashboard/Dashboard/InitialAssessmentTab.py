import dash_html_components as html
from ResultDashboard.Dashboard.DashContent import *
from ResultDashboard.Dashboard.DashPlot import *
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
from datetime import datetime as dt
from ResultDashboard.Dashboard.DashPlot import *
import dash_table



class InitialAssessmentTab:

    def __init__(self, app, DataObject):

        self.app = app
        self.DataObject = DataObject
        # self.DataObject = DataObject
        self.content = html.Div([
            self.FirstLayer(),
        ])

    def FirstLayer(self):
        self.Heading_content = "Initial Load Profile Analysis: Effect of PV on load profile and important statistics"
        self.Detail_content = " Utility often want to know the shape of load profile. Increasing PV penetration affects these load shapes. This tool " \
                              "allows utility to see load profile for different consumer class and also see how the load shape changes" \
                              " when PV penetration increases. Note the PV penetration in this tool is defined based on percentage" \
                              " of peak load of the feeder and is not same as PV scenario defined in other tabs. Also it does take " \
                              "into account the location where they are installed. "

        Col = html.Div([html.Div([Paragraph(self.Heading_content, self.Detail_content).layout()]),
                        html.Div([html.Div([html.H6('Select PV penetration (in %)'),
                                dcc.Slider(id='pv',min=0,max=100,value=0,marks={i: '{}%'.format(i) for i in range(0, 100, 10)},className='h2'),
                                dcc.Graph(id="load-duration-curve", className='mt-5')], className="DropDown"),
                                html.Div([html.H6('Select a day to show load profile: (for year 2018)'),
                                dcc.DatePickerSingle(id='date-picker-single',date=str(dt(2018, 1, 1)), className='h2'), dcc.Graph(id="load-curve",className='mt-3')],
                                className="DropDown"),
                        ]),
                        html.Div([
                            html.Div([html.H6("Important statistics related to load profiles"),dash_table.DataTable(id='table', style_cell={'textAlign': 'left', 'backgroundColor': '#1e2130','color': 'white'},style_as_list_view=True)], className='DropDown')])
                        ])
        return Col

    def layout(self):
        return self.content

    def Callbacks(self):

        @self.app.callback([Output('load-duration-curve','figure'),Output('load-curve','figure'),Output('table','data'),Output('table','columns')],[Input('pv','value'),Input('date-picker-single','date')])
        def UpdateFigureOnAssessmentTab(PVpercentage, Date):

            LoadDuration, DailyLoadProfile, Dataframe = self.DataObject.GetDataDict(PVpercentage,Date)
            return TimeSeriesLinePlot(LoadDuration,mode='lines',stack=True,ylabel='Total Load (kW)').layout(), TimeSeriesLinePlot(DailyLoadProfile,mode='lines',stack=True,ylabel='Total Load (MW)').layout(), Dataframe.to_dict('r'),[{"name": i, "id": i} for i in Dataframe.columns]
