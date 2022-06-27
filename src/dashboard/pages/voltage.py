
# third-party imports
import dash
from dash import html, dcc
import plotly.express as px
import pandas as pd

# internal imports
from utils.utils import get_map_centre


def prepare_voltage_distribution_plot(db_instance, query):


    voltage_bins = db_instance.db.search(query.type=='snapshot_voltage_bins')
    voltage_bins_df = pd.DataFrame()
    
    for voltage_scenario in voltage_bins:
        df = pd.DataFrame(voltage_scenario['data'])
        df['label'] = voltage_scenario['label'] 
        if not voltage_bins_df.empty:
            voltage_bins_df = pd.concat([voltage_bins_df, df])
        else:
            voltage_bins_df = df

    voltage_bin_fig = px.bar(voltage_bins_df, x="Voltage bins", y="Percentage nodes", \
        color="label", barmode="group")

    voltage_bin_fig.update_layout(
            legend={"font": {"color": "white"}},
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font= {"color": "white"}
    )

    return voltage_bin_fig

def prepare_voltage_by_distance_plot(db_instance, query):

    voltage_by_distance = db_instance.db.search(query.type=='snapshot_voltage_by_distance')
    voltage_by_distance_df = pd.DataFrame()
    for voltage_scenario in voltage_by_distance:
        df = pd.DataFrame(voltage_scenario['data'])
        df['label'] = voltage_scenario['label'] 
        if not voltage_by_distance_df.empty:
            voltage_by_distance_df = pd.concat([voltage_by_distance_df, df])
        else:
            voltage_by_distance_df = df

    voltage_by_distance_fig = px.scatter(voltage_by_distance_df, \
        x="Distance from substation (km)", y="Voltage (pu)", 
        color="Phase", symbol="label")


    voltage_by_distance_fig.update_traces(marker_size=3)
    voltage_by_distance_fig.update_layout(
            legend={"font": {"color": "white"}},
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font= {"color": "white"}
    )
    return voltage_by_distance_fig

def prepare_voltage_density_plot(db_instance, query):

    voltage_for_heatmap = db_instance.db.search(query.type=='snapshot_voltage_for_heatmap')[0]['data']

    voltage_for_heatmap_df = pd.DataFrame(voltage_for_heatmap)
    voltage_heatmap_figure = px.density_mapbox(voltage_for_heatmap_df, lat='latitudes', \
        lon='longitudes', z='voltage (pu)', radius=10, 
        center=get_map_centre(
                voltage_for_heatmap['longitudes'],
                voltage_for_heatmap['latitudes']
            ), zoom=15,
        mapbox_style="carto-darkmatter")

    voltage_heatmap_figure.update_layout(
            legend={"font": {"color": "white"}},
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font= {"color": "white"}
    )
    return voltage_heatmap_figure

def generate_voltage_page(db_instance, query):

    voltage_heatmap_figure = prepare_voltage_density_plot(db_instance, query)
    voltage_bin_fig = prepare_voltage_distribution_plot(db_instance, query)
    voltage_by_distance_fig = prepare_voltage_by_distance_plot(db_instance, query)

    layout = html.Div(children=[
        html.H1(children='Voltage Heatmap', className="text-orange-500 my-5 text-xl border-b"),
        html.P(
            children="""Let's see how the voltages are spread in the distribution network""",
            className="mb-3"
        ),

        dcc.Graph(
            id="voltage_heatmap",
            figure=voltage_heatmap_figure,
            className="h-screen"
        ),
        html.H1(children='Histogram of per unit (pu) voltage magnitudes', className="text-orange-500 my-5 text-xl border-b"),
        html.P(
            children="""Understanding voltage distribution of a feeder is first step towards system visibility! This
            plot shows distribution of different voltage bin and corresponding percentage number of nodes in that bin.""",
            className="mb-3"
        ),

        dcc.Graph(
            id="voltage_bin",
            figure=voltage_bin_fig
        ),

        html.H1(children='Voltage distribution by distance from substation', className="text-orange-500 my-5 text-xl border-b"),
        html.P(
            children="""Let's look at how voltage drops with distance in the feeder. The x axis shows distance in km from substation whereas
            y axis shows voltage in per unit (pu)""",
            className="mb-3"
        ),

        dcc.Graph(
            id="voltage_by_distance",
            figure=voltage_by_distance_fig
        ),

    ])

    dash.register_page('voltage', path='/voltage', layout=layout)