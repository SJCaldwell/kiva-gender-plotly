#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Shane Caldwell, Steph Rivera
"""

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import numpy as np

# Import your dataframe from a csv with pandas
df = pd.read_csv('data/kiva_loans.csv')

def split_borrower_gender(l):
    m = 0
    f = 0
    if type(l) != list:
        return np.nan
    for i in l:
        if i== 'male':
            m += 1
        else:
            f += 1
    if m == 0:
        return 'female'
    elif f == 0:
        return 'male'
    else:
        return 'both'

df.borrower_genders = df.borrower_genders.str.split(', ').apply(split_borrower_gender)

top5 = df.groupby('activity').size().sort_values(ascending=False)[0:5]  # lets look at top 5

top5_male = df.groupby('activity').size().sort_values(ascending=False)[0:5]

top5_female = df[df.borrower_genders == 'female'].groupby('activity').size().sort_values(ascending=False)[0:5]

# Create a Dash object instance
app = dash.Dash()

# The layout attribute of the Dash object, app
# is where you include the elements you want to appear in the
# dashboard. Here, dcc.Graph and dcc.Slider are separate
# graph objects. Most of Graph's features are defined
# inside the function update_figure, but we set the id
# here so we can reference it inside update_figure
app.layout = html.Div(className='container', children=[
    html.H1(
        children='Top 5 activities for loans',
        style={
            'textAlign': 'center',  # center the header
            'color': '#7F7F7F'
            # https://www.biotechnologyforums.com/thread-7742.html more color code options
        }
    ),
    html.Div(dcc.Graph(  # add a bar graph to dashboard
        id='basic-interactions',
        figure={
            'data': [
                {
                    'x': top5_male.index,
                    'y': top5_male,
                    'type': 'bar',
                    'opacity': .6  # changes the bar chart's opacity
                }
            ]
        }
            ))
    ])

# Joe scatter-plot
@app.callback(
    dash.dependencies.Output('scatter-with-slider', 'figure'),
    [dash.dependencies.Input('scatter-slider', 'value')])
def update_scatter(selected_year):
    filtered_df = df[df['year'] == selected_year]
    traces = []
    for i in filtered_df.sector.unique():
        df_by_sector = filtered_df[filtered_df['sector'] == i]
        traces.append(go.Scatter(
            x=[np.mean(df_by_sector[df_by_sector['country'] == j].loan_amount) for j in df_by_sector.country.unique()],
            y=[np.mean(df_by_sector[df_by_sector['country'] == j].lender_count) for j in df_by_sector.country.unique()],
            text=df_by_sector['country'],
            mode='markers',
            opacity=0.7,
            marker={
                'size': 15,
                'line': {'width': 0.5, 'color': 'white'}
            },
            name=i
        ))

    return {
        'data': traces,
        'layout': go.Layout(
            xaxis={'type': 'linear', 'title': 'Loan Amount', 'autorange': 'True'},
            yaxis={'type': 'linear', 'title': 'Lender Count', 'autorange': 'True'},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
            legend={'x': 0, 'y': 1},
            hovermode='closest'
        )
    }

if __name__ == '__main__':
    app.run_server(debug=True)
