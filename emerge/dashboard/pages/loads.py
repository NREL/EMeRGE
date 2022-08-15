

import dash
from dash import html, dcc


def generate_load_page(db_instance, query):


    layout = html.Div(children=[
        html.H1(children='Load Heatmap', className="text-orange-500 my-5 text-xl border-b"),
        html.P(
            children="""Let's see how the loads are spread in the distribution network""",
            className="mb-3"
        ),
    ])

    dash.register_page('loads', path='/loads', layout=layout)