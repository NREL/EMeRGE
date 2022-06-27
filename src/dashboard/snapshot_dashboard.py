"""
Using plotly dash to create a dashboard
"""

# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

# third-party imports
from dash import Dash, html, dcc
import plotly.express as px
import pandas as pd
import dash
from tinydb import Query

# internal-impoers
from db.db_handler import TinyDBHandler

import dashboard.pages
from dashboard.pages.voltage import generate_voltage_page
from dashboard.pages.asset_metrics import generate_asset_metrics_page
from dashboard.pages.loads import generate_load_page


def run_server(
    db_path: str,
    debug: bool = True,
    port: int = 8050
):
    db_instance = TinyDBHandler(db_path)
    query = Query()

    external_script = ["https://tailwindcss.com/", 
        {"src": "https://cdn.tailwindcss.com"}]

    app = Dash(__name__,
        external_scripts=external_script, use_pages=True)

    app.scripts.config.serve_locally = True

    generate_voltage_page(db_instance, query)
    generate_asset_metrics_page(db_instance, query)
    generate_load_page(db_instance, query)

    app.layout = html.Div([
        html.H1('EMERGE - Emerging technologies Management and Risk evaluation \
            on distribution Grids Evolution, 2022', className="text-2xl mb-3 text-yellow-400"
        ),

        html.P(children=""" EMERGE is an opensource software product developed at NREL to help increase visibility \
            is distribution network and look at how DERs might impact distribution feeder. We would appreciate if you \
            visit https://github.com/nrel/emerge and give a star to the repo.""", className="mb-3"),

        html.Div(
            [
                html.Div(
                    dcc.Link(
                        f"{page['name']}", href=page["relative_path"],
                        className=""
                    ),
                    className="px-3 mr-10 py-1 bg-sky-600 rounded-md shadow-md hover:bg-indigo-600 hover:cursor-pointer"
                )
                for page in dash.page_registry.values()
            ],
            className="flex justify-center pt-5"
        ),
        dash.page_container
    ], className="bg-slate-800 min-h-screen text-white font-mono p-10")

    app.run_server(debug=debug, port=port)


if __name__ == '__main__':
    
    run_server(r'C:\Users\KDUWADI\Desktop\NREL_Projects\Tunishia\emerge_latest\src\metrics\db.json')