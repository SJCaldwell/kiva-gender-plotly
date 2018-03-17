import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import numpy as np
#from kiva_data_loaders import *

# Import your dataframe from a csv with pandas
df = pd.read_csv("data/kiva_loans.csv")

# converting dates from string to DateTime objects gives nice tools
df['date'] = pd.to_datetime(df['date'])
# for example, we can turn the full date into just a year
df['year'] = df.date.dt.year
# then convert it to integers so you can do list comprehensions later
# astype(int) expects a strings, so we need to go Period -> str -> int
# we want ints so we can find the min, max, etc later
df['year'] = df.year.astype(str).astype(int)

# This is our features of interest
# I grouped by year first so that I can then filter by year with just
# df.loc[2014]
countries_funded_amount = df.groupby(['year', 'country']).size()

# Create a Dash object instance
app = dash.Dash()

# The layout attribute of the Dash object, app
# is where you include the elements you want to appear in the
# dashboard. Here, dcc.Graph and dcc.Slider are separate
# graph objects. Most of Graph's features are defined
# inside the function update_figure, but we set the id
# here so we can reference it inside update_figure
app.layout = html.Div([
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


if __name__ == '__main__':
    app.run_server()