
# third-party imports
import dash
from dash import html, dcc
from matplotlib.pyplot import legend
import plotly.graph_objects as go

# internal imports
from utils.utils import get_map_centre



def prepare_network_plot(db_instance, query):
    coordinates = db_instance.db.search(query.type=='coordinates')[0]['data']
    feeder_network_data = []
    feeder_network_data.append(
        go.Scattermapbox(
                mode="markers",
                lon=coordinates['nodes']['longitudes'],
                lat=coordinates['nodes']['latitudes'],
                marker={'size': 2, "color": "blue"},
                )
    )

    feeder_network_data.append(
        go.Scattermapbox(
                mode="markers+lines",
                lon=coordinates['edges']['longitudes'],
                lat=coordinates['edges']['latitudes'],
                marker={'size': 0},
                line={"color": "red"},

                )
    )

    fig = go.Figure(data=feeder_network_data)
    fig.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            legend={"font": {"color": "white"}},
            paper_bgcolor="#0f172a",
            showlegend=False
    )
    fig.update_mapboxes({
        "accesstoken": None,
        "style": "carto-darkmatter",
        "center": get_map_centre(
                coordinates['nodes']['longitudes'],
                coordinates['nodes']['latitudes']
            ),
        "zoom": 15
        })
    return fig

def generate_asset_metrics_page(db_instance, query):

    asset_metrics = db_instance.db.search(query.type=='asset_metrics')[0]['metrics']
    metrics_div_contents = [
        html.Div([
            html.H1(children=f"{key}", className="bg-slate-900 px-3 py-2 uppercase"),
            html.Div([
                html.Div([
                                html.H1(children=f"{metric_name}:", className="mr-5"),
                                html.H1(children=f"{metric_value}", className="text-orange-500")
                            ], className="flex justify-between md:grid md:grid-cols-2 mb-2")
                    for metric_name, metric_value in metric_dict.items()
            ], className="p-5 grid grid-cols-1 md:grid-cols-2"),
        ], className="bg-slate-700 border-1 border-white shadow-md mb-5 mt-5") for key, metric_dict in asset_metrics.items()
    ]

    fig = prepare_network_plot(db_instance, query)

    layout = html.Div(children=[
        html.H1(children='Feeder network', className="text-xl mb-3 mt-5 font-bold text-orange-500 border-b"),
        html.P(children=""" Let's see how your feeder looks like. """, className="mb-3"),
        dcc.Graph(
            id='feeder-network',
            figure=fig,
            className="h-screen"
        ),
        html.H1(children='Asset Metrics', className="text-xl mb-3 mt-5 font-bold text-orange-500 border-b"),
        *metrics_div_contents

    ])

    dash.register_page('asset_metrics', path='/', layout=layout)