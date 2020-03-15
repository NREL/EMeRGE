"""
author: Kapil Duwadi
version: 0.0.1
"""
from dash.dependencies import Input, Output, State
import dash_html_components as html
from ResultDashboard.Dashboard.DashContent import *
from ResultDashboard.Dashboard.DistMetricPVTab import *
from ResultDashboard.Dashboard.PVConnectionTab import *
from ResultDashboard.Dashboard.DistMetricTabAdvancedPV import *
from ResultDashboard.Dashboard.InitialAssessmentTab import *


class CreateApp:

    def __init__(self,app,DashboardSettings, DataObject, PVDataObject, InitialAssessmentObject):

        self.app = app

        self.DataObject = DataObject
        self.DataObjectforAdvancedPV = PVDataObject
        self.InitialAssessmentObject = InitialAssessmentObject

        self.DashboardSettings  =DashboardSettings

        self.DistMetricAdvancedPVObject = DistMetricAdvancedPVTab(self.app,self.DataObjectforAdvancedPV)
        self.DisMetricPVObject = DistMetricPVTab(self.app,self.DataObject)
        self.PVConnectionObject = PVConnectionTab(self.app,self.DataObject,self.DashboardSettings)
        self.InitialAssessmentObject = InitialAssessmentTab(self.app,self.InitialAssessmentObject)

        # Start Creating layout
        self.app.layout = html.Div(children=[

            # Top Banner Layer
            self.TopBanner(),

            # Create Tabs
            self.CreateTabs(),

            # Create Context for Tab
            self.Content()
        ])


    def Content(self):
        return html.Div(id="Tab-content",children=[])

    def Callbacks(self):
        self.UpdateOnTab()
        self.DisMetricPVObject.Callbacks()
        self.PVConnectionObject.Callbacks()
        self.InitialAssessmentObject.Callbacks()

    def UpdateOnTab(self):
        @self.app.callback(Output("Tab-content", "children"), [Input("DashTab", "value")])
        def Update_Render(tab):
            print(tab)
            if tab == 'Classical PV':
                return self.DisMetricPVObject.layout()
            if tab =='PV Connection Request':
                return self.PVConnectionObject.layout()
            if tab == 'Advanced PV':
                return self.DistMetricAdvancedPVObject.layout()
            if tab == 'Initial Assessment':
                return self.InitialAssessmentObject.layout()

    def TopBanner(self):

        TopContent = "{} : Distribution System Analysis Dashboard".format(self.DashboardSettings['Active Project'])

        BottomContent  = "Framework to visualize system level and asset level metrics to inform decision making "

        return Banner(self.app,TopContent,BottomContent,'logo.png').layout()

    def CreateTabs(self):

        TabNames = ["Initial Assessment","PV Connection Request","Classical PV","Advanced PV","EV",]

        return Tabs(TabNames,'DashTab').layout()

    def layout(self):

        return self.app.layout