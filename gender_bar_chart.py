#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar  7 19:18:43 2018

@author: beaubritain, Richard Decal
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

##### Beau graphs
# subset for important columns
"""df = df[['term_in_months', 'loan_amount', 'lender_count', 'funded_amount',
         'borrower_genders', 'repayment_interval', 'country', 'date',
         'activity']]"""
# subset for top 2 (number of loans) country values and USA to compare to
country_values = ['Philippines', 'Kenya', 'United States']
Beau_df = df[df['country'].isin(country_values)]
# sample to improve speed
a = Beau_df.sample(5000)

# len(kiva.activity.unique()) #shows there are 163 unique activities

top5 = df.groupby('activity').size().sort_values(ascending=False)[0:5]  # lets look at top 5

top5_male = df.groupby('activity').size().sort_values(ascending=False)[0:5]

top5_female = df[df.borrower_genders == 'female'].groupby('activity').size().sort_values(ascending=False)[0:5]
######## /Beau graphs


###### Richard maps
# converting dates from string to DateTime objects gives nice tools
df['date'] = pd.to_datetime(df['date'])
# for example, we can turn the full date into just a year
df['year'] = df.date.dt.year
# then convert it to integers so you can do list comprehensions later
# astype(int) expects a strings, so we need to go Period -> str -> int
# we want ints so we can find the min, max, etc later
df['year'] = df.year.astype(str).astype(int)

# This is our features of interest for mapping
# I grouped by year first so that I can then filter by year simply with just
# df.loc[2014]
countries_funded_amount = df.groupby(['year', 'country']).size()
######

# Create a Dash object instance
app = dash.Dash()

# The layout attribute of the Dash object, app
# is where you include the elements you want to appear in the
# dashboard. Here, dcc.Graph and dcc.Slider are separate
# graph objects. Most of Graph's features are defined
# inside the function update_figure, but we set the id
# here so we can reference it inside update_figure
app.layout = html.Div(className='container', children=[
    html.H1(children='Top 3 countries Violin distributions',  # add a title
            style={
                'textAlign': 'center',  # center the header
                'color': '#7F7F7F'
                # https://www.biotechnologyforums.com/thread-7742.html more color code options
            }),
    html.Hr(),
    html.Div(className='two columns', children=[
        dcc.RadioItems(  # buttons that select which y value in violin plots
            id='items',
            options=[
                {'label': 'term in months', 'value': 'term_in_months'},
                {'label': 'loan amount', 'value': 'loan_amount'},
                {'label': 'lender count', 'value': 'lender_count'},
                {'label': 'funded amount', 'value': 'funded_amount'}
            ],
            value='term_in_months',
            style={'display': 'block',
                   'textAlign': 'center',
                   'color': '#7FDBFF'}
        ),
        html.Hr(),
        dcc.RadioItems(  # more options
            id='points',
            options=[
                {'label': 'Display All Points', 'value': 'all'},
                {'label': 'Hide Points', 'value': False},
                {'label': 'Display Outliers', 'value': 'outliers'},
                {'label': 'Display Suspected Outliers',
                 'value': 'suspectedoutliers'},
            ],
            value='all',
            style={'display': 'block',
                   'textAlign': 'center',
                   'color': '#7FDBFF'}
        ),
    ]),
    html.Div(dcc.Graph(id='graph'), className='ten columns'),
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

            ],
            'layout': go.Layout(
                xaxis={'title': 'Activity'},
                yaxis={'title': 'Count'},
            )
        }

    )),
    # Richard's cloropleth map
    html.Div([
        html.Hr(),
        html.H1(
        children='Cloropleth maps including slider and log-scale colormap',
        style={
            'textAlign': 'center',  # center the header
            'color': '#7F7F7F'
            # https://www.biotechnologyforums.com/thread-7742.html more color code options
        }
    ),
        dcc.Graph(id='graph-with-slider'),
        html.Div([  # div inside div for style
            dcc.Slider(
                id='year-slider',
                min=df['year'].min(),
                max=df['year'].max(),
                value=df['year'].min(),  # The default value of the slider
                step=None,
                # the values have to be the same dtype for filtering to work later
                marks={str(year): year for year in df['year'].unique()},
            )
        ],
            style={'marginLeft': 40, 'marginRight': 40})
    ]),
        html.Div([
        dcc.Graph(id='scatter-with-slider', animate='true'),
        dcc.Slider(
            id='scatter-slider',
            min=2014,
            max=2017,
            value=2014,
            step=1,
            marks={str(year): str(year) for year in [2014, 2015, 2016, 2017]}
    )
])
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
