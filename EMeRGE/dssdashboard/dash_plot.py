
import plotly.graph_objects as go

def timeseries_plot(data_dict,stack=False,ylabel='',title='',marker={'size':10},mode='lines+markers'):

    plots = []
    for keys, values in data_dict.items():
        if keys != 'TimeStamp':
            if stack==True:
                plots.append(go.Scatter(x=data_dict['TimeStamp'], 
                                        y=values, 
                                        mode=mode, 
                                        name=keys,
                                        marker=marker,
                                        stackgroup='one'))
            else:
                plots.append(go.Scatter(x=data_dict['TimeStamp'], 
                                        y=values, 
                                        mode=mode, 
                                        name=keys,
                                        marker={'size': 10}))
    plot_layout = go.Layout(plot_bgcolor="#1e2130",
                            paper_bgcolor="#1e2130",
                            font={'color': '#7FDBFF'},
                            xaxis={'showgrid': False,'zerolinewidth':0.5},
                            yaxis={'title': ylabel, 'showgrid': False,'zerolinewidth':0.5},
                            title=title,
                            legend={'orientation':'h','y':1.2},
                            margin=dict(r=20, t=60))

    return go.Figure(data=plots,layout=plot_layout)

def line_plot(data_dict,ylabel='',title=''):

    plots = []
    for keys, values in data_dict.items():
        if keys != 'x_val' and keys != 'Scenarios':
            plots.append(go.Scatter(x=data_dict['x_val'], 
                                    y=values, 
                                    mode='lines+markers', 
                                    name=keys,
                                    marker={'size': 10}))
    plot_layout = go.Layout(plot_bgcolor="#1e2130",
                            paper_bgcolor="#1e2130",
                            font={'color': '#7FDBFF'},
                            xaxis={'tickvals': data_dict['x_val'], \
                                'ticktext': data_dict['Scenarios'],'showgrid': False, \
                                'zerolinewidth':0.5},
                            yaxis={'title': ylabel, 'showgrid': False,'zerolinewidth':0.5},
                            title=title,
                            legend={'orientation':'h','y':1.2},
                            margin=dict(r=20, t=60))

    return go.Figure(data=plots,layout=plot_layout)

def geo_scatter_map(lines_lat,lines_lon, scatter_x,scatter_y ,centerx,centery, 
                marker={'color':"#FF0000",'opacity':1.0,'size':10},
                hoverinfo='all',hovertext='',height=400,zoom=13):

    plot =  [  go.Scattermapbox(   lat=lines_lat, 
                                    lon=lines_lon, 
                                    mode='lines',
                                    line=dict(width=1.5, color='#FFFF00')
                                ),
                go.Scattermapbox(   lat=scatter_x, 
                                    lon=scatter_y,
                                    mode='markers',
                                    marker=marker,
                                    hovertext = hovertext,
                                    hoverinfo = hoverinfo,)
            ]
    plot_layout =  go.Layout(   autosize=True,
                                height=height,
                                margin=go.layout.Margin(l=0, r=0, t=0, b=0),
                                mapbox=dict(
                                            center=dict(lat=centerx, 
                                                        lon=centery),
                                            style="carto-darkmatter", 
                                            zoom=zoom),
                                plot_bgcolor="#171b26",
                                paper_bgcolor="#171b26",
                                showlegend=False)

    return go.Figure(data=plot,layout=plot_layout)