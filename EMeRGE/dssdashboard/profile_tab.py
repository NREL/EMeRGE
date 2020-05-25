# Standard libraries
from datetime import datetime as dt

# External libraries
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output, State

# Internal libraries
from dssdashboard.constants import PROFILE_TEXTS
from dssdashboard.dash_content import create_paragraph
from dssdashboard.dash_plot import timeseries_plot

class CreateProfileTab:

    def __init__(self, app, data_object, settings, logger):

        self.app = app
        self.data_object = data_object
        self.settings = settings
        self.logger = logger

        self.content = html.Div([
            self.first_row(),
        ])

        self.logger.info('Profile tab instantiated ...')
    
    def first_row(self):

        col = html.Div([html.Div([create_paragraph(PROFILE_TEXTS['first_layer']['heading'], 
                                            PROFILE_TEXTS['first_layer']['detail'])]), 
                        html.Div([
                            html.Div([
                                html.H6('Select PV penetration (in %)'),
                                dcc.Slider(id='pv',
                                            min=0,
                                            max=100,
                                            value=0,
                                            marks={i: '{}%'.format(i) for i in range(0, 100, 10)},className='h2'),\
                                dcc.Graph(id="load-duration-curve", className='mt-5')], className="DropDown"),
                            html.Div([
                                html.H6('Select a day to show load profile:'),
                                dcc.DatePickerSingle(
                                    id='date-picker-single',
                                    date=str(dt(self.settings['year'], 1, 1)), className='h2'), 
                                    dcc.Graph(id="load-curve",className='mt-3')],
                                className="DropDown"),
                        ]),
                        html.Div([
                            html.Div([html.H6("Important statistics related to load profiles"),
                            dash_table.DataTable(
                                id='table', 
                                style_cell={'textAlign': 'left', 'backgroundColor': '#1e2130','color': 'white'},
                                style_as_list_view=True)], className='DropDown')])
                        ])

        return col

    def layout(self):
        return self.content

    def call_backs(self):

        @self.app.callback([Output('load-duration-curve','figure'),Output('load-curve','figure'), \
                Output('table','data'),Output('table','columns')], \
                [Input('pv','value'),Input('date-picker-single','date')])
        def update_fig_in_profiletab(pv_percen, date):
            
            self.logger.info(f'Processing load profile for date {date} and PV percentage (pv_percen)')
            
            load_duration, daily_data, stats = self.data_object.get_data(pv_percen,date)
            
            return timeseries_plot(load_duration,mode='lines',stack=True,ylabel='Total Load (kW)'), \
                    timeseries_plot(daily_data,mode='lines',stack=True,ylabel='Total Load (MW)'), \
                    stats.to_dict('r'),[{"name": i, "id": i} for i in stats.columns]


