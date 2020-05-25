# Standard libraries
import os

# External libraries
import dash_html_components as html
from dash.dependencies import Input, Output, State

# Internal libraries
from dssdashboard.constants import HEADER_TITLE, HEADER_DETAIL, TABLIST
from dssdashboard.dash_content import create_banner, create_tabs, create_paragraph
from dssdashboard.profile_tab import CreateProfileTab
from dssdashboard.pv_tab import CreatePVtab
from dssdashboard.pv_connection_tab import PVconnectionTab


class CreateApp:

    def __init__(self,app, settings, logger, 
                    profile=None, pv_object=None, advanced_pv_object=None, coord_object=None):

        self.app = app
        self.settings = settings
        self.logger = logger
        self.profile_object = profile
        self.pv_object = pv_object
        self.coord_object = coord_object
        self.advanced_pv_object = advanced_pv_object

        self.active_project = os.path.join(self.settings['project_path'],self.settings['active_project'])
        
        if self.profile_object != None:
            self.profiletab = CreateProfileTab(self.app,self.profile_object,
                                self.settings,self.logger)

        if self.pv_object !=None and self.coord_object != None:
            self.pvtab = CreatePVtab(self.app,self.pv_object,self.coord_object,
                                    self.settings,self.logger,'classical')
        
        if self.advanced_pv_object !=None  and self.coord_object != None:
            self.advanced_pvtab = CreatePVtab(self.app,self.pv_object,self.coord_object,
                            self.settings,self.logger,'advanced')

        if 'PVConnection' in os.listdir(self.active_project) and self.coord_object != None:
            self.pvcon_tab = PVconnectionTab(self.app,self.coord_object, 
                            self.settings,self.logger)
        
        # Create a layout 
        self.app.layout = html.Div( children=[
            self.top_banner(),
            self.tabs(),
            self.content()
        ])

    def content(self):
        return html.Div(id='tab-content')

    def update_on_tab(self):
        
        # update tab content
        @self.app.callback(Output('tab-content','children'),[Input("dashtab","value")])
        def update_render(tab): 
            self.logger.info(f'{tab} clicked')
            if tab == 'Classical PV':
                if self.pv_object != None and self.coord_object != None:
                    return self.pvtab.layout()

            if tab == 'Advanced PV':
                if self.advanced_pv_object != None and self.coord_object != None:
                    return self.advanced_pvtab.layout()
                
            if tab == 'PV Connection Request':
                if 'PVConnection' in os.listdir(self.active_project) and self.coord_object != None:
                    return self.pvcon_tab.layout() 

            if tab == 'Initial Assessment':
                if self.profile_object != None:
                    return self.profiletab.layout()
    
    def call_backs(self):

        self.update_on_tab()
        if self.profile_object != None:
            self.profiletab.call_backs()
        if self.pv_object != None and self.coord_object != None:
            self.pvtab.call_backs()
        if self.advanced_pv_object != None and self.coord_object != None:
            self.advanced_pvtab.call_backs()
        if 'PVConnection' in os.listdir(self.active_project) and self.coord_object != None:
            self.pvcon_tab.call_backs()
    
    def top_banner(self):

        self.logger.info('Creating top banner ........')
        return create_banner(self.app,HEADER_TITLE,HEADER_DETAIL,'logo.png')

    def tabs(self):

        self.logger.info('Creating tabs ........')
        return create_tabs(TABLIST, 'dashtab')

    def layout(self):

        return self.app.layout