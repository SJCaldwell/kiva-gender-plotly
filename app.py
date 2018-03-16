import dash
import dash_core_components as dcc
from dash.dependencies import Input, Output
import dash_html_components as html
import numpy as np
import pandas as pd
import plotly.graph_objs as go

df = pd.read_csv("./data/kiva_loans.csv", parse_dates=True)

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

df['disbursed_year'] = pd.to_datetime(df.disbursed_time).dt.year
top5 = df.groupby('activity').size().sort_values(ascending=False)[0:5]  # lets look at top 5
top5_male = df.groupby('activity').size().sort_values(ascending=False)[0:5]
top5_female = df[df.borrower_genders == 'female'].groupby('activity').size().sort_values(ascending=False)[0:5]

app = dash.Dash()
app.layout = html.Div(className='container', children=[
    html.Div([dcc.Graph(id='gender-by-sector'),
    dcc.Slider(id='date-slider',
               min=df.disbursed_year.min(),
               max=df.disbursed_year.max(),
               value=df.disbursed_year.min(),
               marks={str(year): str(year) for year in [2013, 2014, 2015, 2016,
                                                        2017]}
              )], style={'marginLeft': 50, 'marginRight': 50}),
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
    Output('gender-by-sector', 'figure'),
    [Input('date-slider', 'value')])
def update_gender_by_sector(selected_year):

    gensec = df[df.disbursed_year==selected_year].groupby('borrower_genders')['sector'].value_counts()
    gensec = gensec.unstack().transpose()

    gensec = gensec.apply(lambda row: row/gensec.sum(1))


    trace_male = go.Bar(x=gensec.index, y=gensec.male, name='Male')
    trace_female = go.Bar(x=gensec.index, y=gensec.female, name='Female')
    trace_both = go.Bar(x=gensec.index, y=gensec.both, name='Mixed')

    data = [trace_male, trace_female, trace_both]
    layout = go.Layout(
        title='Percent of loans by sector by gender',
        barmode='stack'
    )
    return {
        'data': data,
        'layout': layout
    }

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
                    'opacity': .6,
                    "color": "rgb(30, 55, 5)"
                }
            ]
        }



if __name__ == "__main__":
    app.run_server(debug=True)
