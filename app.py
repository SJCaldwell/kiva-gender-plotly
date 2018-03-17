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


# converting dates from string to DateTime objects gives nice tools
df['date'] = pd.to_datetime(df['date'])
# for example, we can turn the full date into just a year
df['year'] = df.date.dt.year
# then convert it to integers so you can do list comprehensions later
# astype(int) expects a strings, so we need to go Period -> str -> int
# we want ints so we can find the min, max, etc later
df['year'] = df.year.astype(str).astype(int)

countries_funded_amount = df.groupby(['year', 'country']).size()

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
        style={'marginLeft':40, 'marginRight':40})
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


# Notice the Input and Outputs in this wrapper correspond to
# the ids of the components in app.layout above.
@app.callback(
    Output('graph-with-slider', 'figure'),
    [Input('year-slider', 'value')])
def update_figure(selected_year):
    """Define how the graph is to be updated based on the slider."""

    # Depending on the year selected on the slider, filter the db
    # by that year.

    # snag: using .groupby() with more than one feature caused the datatype
    # to be Pandas.Series instead of Pandas.DataFrame. So, we couldn't just do
    # countries_funded_amount[countries_funded_amount['year'] == selected_year]
    one_year_data = countries_funded_amount.loc[selected_year]

    logzMin = np.log(one_year_data.values.min())
    logzMax = np.log(one_year_data.values.max())
    log_ticks = np.linspace(logzMin, logzMax, 8)
    exp_labels = np.exp(log_ticks).astype(np.int, copy=False)
    data = [dict(
        type='choropleth',
        locations=one_year_data.index.get_level_values('country'),  # list of country names
        # other option is USA-states
        locationmode='country names',
        # sets the color values. using log scale so that extreme values don't
        # drown out the rest of the data
        z=np.log(one_year_data.values),  # ...and their associated values
        # sets the text element associated w each position
        text=one_year_data.values,
        hoverinfo='location+text',  # hide the log-transformed data values
        # other colorscales are available here:
        # https://plot.ly/ipython-notebooks/color-scales/
        colorscale='Greens',
        # by default, low numbers are dark and high numbers are white
        reversescale=True,
        # set upper bound of color domain (see also zmin)
        #zmin=200,
        #zmax=30000,
        # if you want to use zmin or zmax don't forget to disable zauto
        #zauto=False,
        marker={'line': {'width': 0.5}},  # width of country boundaries
        colorbar={'autotick': True,
                  'tickprefix': '',  # could be useful if plotting $ values
                  'title': '# of loans',  # colorbar title
                  'tickvals': log_ticks,
                  'ticktext': exp_labels  # transform log tick labels back to standard scale
                  },
    )]
    layout = dict(
        title='Total Loans Per Country. Year: {}<br>Source:\
                <a href="https://www.kaggle.com/kiva/data-science-for-good-kiva-crowdfunding"">\
                Kaggle</a>'.format(selected_year),
        font=dict(family='Courier New, monospace', size=18, color='#7f7f7f'),
        geo={'showframe': False}  # hide frame around map
    )
    fig = {'data': data, 'layout': layout}
    return fig


if __name__ == "__main__":
    app.run_server(debug=True)
