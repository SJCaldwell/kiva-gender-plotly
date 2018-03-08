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

app = dash.Dash()
app.layout = html.Div(className='container', children=[
    html.Div([dcc.Graph(id='gender-by-sector'),
    dcc.Slider(id='date-slider',
               min=df.disbursed_year.min(),
               max=df.disbursed_year.max(),
               value=df.disbursed_year.min(),
               marks={str(year): str(year) for year in [2013, 2014, 2015, 2016,
                                                        2017]}
              )], style={'marginLeft': 50, 'marginRight': 50})
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


if __name__ == "__main__":
    app.run_server(debug=True)
