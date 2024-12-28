import pandas as pd
import io
import base64
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import os
import plotly.express as px
import plotly.graph_objects as go

# Initialize Dash app
app = dash.Dash(__name__)
app.title = "MCE Placement Visualizer"

# Layout for the dashboard
app.layout = html.Div([
    html.H1("MCE Placement Visualizer", style={'textAlign': 'center'}),
    dcc.Dropdown(
        id='year-dropdown',
        options=[{'label': f'data{year}-{year+1}', 'value': f'data{year}-{year+1}'} for year in range(2015, 2024)],
        placeholder="Select a batch year",
        style={'width': '50%', 'margin': '0 auto', 'padding': '10px'}
    ),
    html.Div(id='error-message', style={'color': 'red', 'textAlign': 'center', 'margin': '10px'}),
    html.Div(
        id='visualization-content',
        style={'display': 'flex', 'flexDirection': 'column', 'alignItems': 'center', 'gap': '20px'}
    )
])

# Helper function to create line graph using Plotly
def plot_highest_package_plotly(data):
    branches = ['EC', 'CS', 'IS', 'EI', 'EE', 'MECH', 'AUTO', 'IP', 'CIVIL']
    branch_max_package = {}

    for branch in branches:
        if branch in data.columns:
            branch_max_package[branch] = data[branch].max()

    # Creating a Plotly figure
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=list(branch_max_package.keys()),
            y=list(branch_max_package.values()),
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(size=8),
            name='Highest Package'
        )
    )

    fig.update_layout(
        title="Highest Package for Each Branch",
        xaxis_title="Branches",
        yaxis_title="Highest Package (LPA)",
        template="plotly",
        width=900,
        height=500
    )

    return fig

# Callback to update visualizations based on year
@app.callback(
    [Output('visualization-content', 'children'),
     Output('error-message', 'children')],
    [Input('year-dropdown', 'value')]
)
def update_visualizations(selected_year):
    if not selected_year:
        return None, "Please select a batch year."
    
    file_name = f"{selected_year}.csv"
    
    if not os.path.exists(file_name):
        return None, f"Error 404: File '{file_name}' not found."
    
    # Load the data
    data = pd.read_csv(file_name)
    
    # Data preprocessing
    if not {'Company Name/CTC IN LPA/Date of drive', 'Total'}.issubset(data.columns):
        return None, "Error: Required columns are not found in the dataset."

    # Pie Chart: Branch-wise placement distribution
    branches = ['EC', 'CS', 'IS', 'EI', 'EE', 'MECH', 'AUTO', 'IP', 'CIVIL']
    branch_totals = data[branches].sum().reset_index()
    branch_totals.columns = ['Branch', 'Total Placements']
    pie_chart = px.pie(
        branch_totals, names='Branch', values='Total Placements',
        title="Branch-wise Placement Distribution",
        template='plotly'
    )
    pie_chart.update_layout(width=800, height=500)

    # Line Graph: Highest Package for Each Branch
    highest_package_graph = plot_highest_package_plotly(data)

    # Bar Chart: Total placements per company
    bar_chart = px.bar(
        data,
        x='Company Name/CTC IN LPA/Date of drive',
        y='Total',
        title="Total Placements Per Company",
        labels={'Company Name/CTC IN LPA/Date of drive': 'Company', 'Total': 'Total Placements'},
        template='plotly'
    )
    bar_chart.update_layout(width=900, height=500)

    # Render graphs
    return [
        dcc.Graph(figure=pie_chart),
        dcc.Graph(figure=highest_package_graph),
        dcc.Graph(figure=bar_chart)
    ], None

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
