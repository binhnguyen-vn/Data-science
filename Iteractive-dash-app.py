# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Tạo drop down list
dropdown_options = [
    {'label': 'All Sites', 'value': 'ALL'},
    {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
    {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
    {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
    {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
]

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                    dcc.Dropdown(
                                        id='site-dropdown',
                                        options=dropdown_options,
                                        value='ALL',            # Giá trị mặc định
                                        placeholder='Select a Launch Site',
                                        searchable=True
                                    ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(
                                    id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
                                    value=[min_payload, max_payload]
                                ),
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Tổng số lần phóng thành công theo mỗi launch site
        success_counts = spacex_df[spacex_df['class'] == 1].groupby('Launch Site').size().reset_index(name='count')
        fig = px.pie(success_counts, names='Launch Site', values='count',
                     title='Total Successful Launches by Site')
    else:
        # Số lần thành công vs thất bại tại một site cụ thể
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        site_counts = site_data['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        site_counts['class'] = site_counts['class'].map({1: 'Success', 0: 'Failed'})
        fig = px.pie(site_counts, names='class', values='count',
                     title=f'Success vs Failed Launches for {selected_site}')
    return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_plot(selected_site, payload_range):
    low, high = payload_range

    # Lọc dữ liệu theo khoảng payload
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title='Payload vs Outcome for All Sites',
                         hover_data=['Launch Site'])
    else:
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        fig = px.scatter(site_df,
                         x='Payload Mass (kg)', y='class',
                         color='Booster Version Category',
                         title=f'Payload vs Outcome for {selected_site}',
                         hover_data=['Launch Site'])

    return fig

# Run the app
if __name__ == '__main__':
    app.run()
