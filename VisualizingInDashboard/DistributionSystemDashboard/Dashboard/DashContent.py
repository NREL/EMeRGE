"""
author: Kapil Duwadi
version: 0.0.1
"""
import dash_html_components as html
import dash_core_components as dcc


class Banner:

    def __init__(self,app, H5content='', H6content='',logo=''):

        self.app = app
        if logo == '':
            self.Banner =  html.Div(
                className = "banner",
                children = [
                    html.Div(children=[
                        html.H5(H5content), html.H6(H6content)
                ])
            ])
        else:
            self.Banner =  html.Div(
                className="banner",
                children=[
                    html.Div(children=[
                        html.H5(H5content), html.H6(H6content)
                    ]),
                    html.Div(id="banner-logo",
                             children=[html.Img(id="logo", src=self.app.get_asset_url("logo.png")),],)
                ])

    def layout(self):

        return self.Banner

class Tabs:

    def __init__(self,TabNameList, TabID):

        self.Tabs = html.Div([dcc.Tabs(id=TabID, value=TabNameList[0],
                             children= [dcc.Tab(label=tab,
                                                value=tab,
                                                style={'padding':'6px','fontWeight':'bold','border-style':'none'},
                                                selected_style={'borderTop': '1px solid #d6d6d6','fontWeight':'bold','borderBottom': '1px solid #d6d6d6','backgroundColor': '#119DFF','color': 'white','padding': '6px'}
                                                ) for tab in TabNameList],style={'height':'35px','color':'#000000','margin':'0px 0px 0px 0px','box-shadow': '1px 1px 0px white'})])

    def layout(self):

        return self.Tabs


class Paragraph:

    def __init__(self, Heading, Details):

        self.content = html.Div([
            html.H2(Heading),
            html.H5(Details)
        ],className='Paragraph')

    def layout(self):
        return self.content



