# External libraries
import dash_html_components as html
import dash_core_components as dcc


def create_banner(app, H5content='', H6content='',logo=''):
    
    if logo == '':
        banner =  html.Div(
            className = "banner",
            children = [
                html.Div(children=[
                    html.H5(H5content), html.H6(H6content)
            ])
        ])
    else:
        banner =  html.Div(
            className="banner",
            children=[
                html.Div(children=[
                    html.H5(H5content), html.H6(H6content)
                ]),
                html.Div(id="banner-logo",
                            children=[html.Img(id="logo", src=app.get_asset_url(logo)),],)
            ])

    return banner

def create_tabs(tablist,tabid):

    return html.Div([
               dcc.Tabs(id=tabid, 
                        value=tablist[0],
                        children= [
                            dcc.Tab(label=tab,
                            value=tab,
                            style={'padding':'6px','fontWeight':'bold','border-style':'none'},
                            selected_style={'borderTop': '1px solid #d6d6d6','fontWeight':'bold',
                                'borderBottom': '1px solid #d6d6d6','backgroundColor': '#119DFF',
                                'color': 'white','padding': '6px'}
                                ) 
                            for tab in tablist],
                            style={'height':'35px','color':'#000000','margin':'0px 0px 0px 0px',
                            'box-shadow': '1px 1px 0px white'}
                        )
                    ])

def create_paragraph(heading,detail):

    content =   html.Div([
            html.H2(heading),
            html.H5(detail)
        ],className='Paragraph')
    
    return content
