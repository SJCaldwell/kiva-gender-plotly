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
        id='top5-by-gender',
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
            )),
    
    html.Label('Gender'),
    dcc.RadioItems(
        id = 'gender-radio',
        options=[
            {'label': 'Male', 'value': 'male'},
            {'label': 'Female', 'value': 'female'},
            {'label': 'Both', 'value': 'both'}
        ],
        value='both'
    )
    ])

@app.callback(
    dash.dependencies.Output('top5-by-gender', 'figure'),
    [dash.dependencies.Input('gender-radio', 'value')])
def update_barchart(gender):
    top5 = df[df.borrower_genders == gender].groupby('activity').size().sort_values(ascending=False)[0:5]
    return {
            'data': [
                {
                    'x': top5.index,
                    'y': top5,
                    'type': 'bar',
                    'opacity': .6
                }
            ]
        }

if __name__ == '__main__':
    app.run_server(debug=True)
