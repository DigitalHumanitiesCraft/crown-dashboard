import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
from urllib.parse import quote as url_quote


# Load data
objects_df = pd.read_excel('data/CROWN_Objects_1_2024_02_02.xlsx')
userfields_df = pd.read_excel('data/crown-userfields.xlsx')

# Preprocess data
def process_medium_types(medium_string):
    if pd.isna(medium_string):
        return []
    return [m.strip() for m in medium_string.split(';') if m.strip()]

medium_types = objects_df['Medium'].apply(process_medium_types).explode()
medium_counts = medium_types.value_counts().reset_index()
medium_counts.columns = ['Medium_Type', 'Count']

# Extract unique categories dynamically from the data
unique_mediums = medium_counts['Medium_Type'].unique()
unique_categories = {um.strip().lower(): um.strip().capitalize() for um in unique_mediums}

# Function to categorize medium types dynamically
def categorize_medium(medium_type):
    medium_list = medium_type.split(';')
    categorized_list = []
    for medium in medium_list:
        medium_cleaned = medium.strip().lower()
        categorized_list.append(unique_categories.get(medium_cleaned, 'Other'))
    return '; '.join(categorized_list)

# Apply the function to the medium counts
medium_counts['Category'] = medium_counts['Medium_Type'].apply(categorize_medium)

# Extract and count enamel colors from userfields_df
color_columns = [col for col in userfields_df.columns if any(color in col.lower() for color in ['color', 'farbe', 'transparent', 'blau', 'rot', 'gelb', 'grün', 'schwarz', 'weiß', 'braun', 'rosa', 'lila', 'violett', 'orange'])]

# Convert all values to strings
userfields_df[color_columns] = userfields_df[color_columns].astype(str)

# Clean up and count unique colors
color_data = userfields_df[color_columns].apply(lambda x: x.str.strip().replace({'nan': None})).apply(pd.Series.value_counts).fillna(0)
unique_colors = color_data.index[color_data.sum(axis=1).astype(bool)]

# Further clean color names for visualization
cleaned_colors = [color.split(';')[0].strip() for color in unique_colors if isinstance(color, str) and color not in ['0.0', '1.0', '(auswählen)']]
color_counts = pd.Series(cleaned_colors).value_counts().reset_index()
color_counts.columns = ['Color', 'Count']

# Create the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose the Flask server

# Define the navigation bar
nav_bar = html.Div([
    dcc.Link('Home', href='/', className='nav-link'),
    dcc.Link('Specialized Data Exploration', href='/specialized', className='nav-link')
], className='nav-bar')

# Home page layout
home_page_layout = html.Div([
    nav_bar,
    html.H1("CROWN Data Dashboard (~95% AI generated)"),
    
    html.Div([
        html.Label("Select Object via Medium"),
        dcc.Dropdown(
            id='category-dropdown',
            options=[{'label': cat, 'value': cat} for cat in medium_counts['Category'].unique()],
            value=medium_counts['Category'].unique().tolist(),
            multi=True
        ),
    ]),
    
    dcc.Graph(id='object-distribution-chart'),
    
    html.Div(id='summary-stats'),

    html.Div(id='click-data', style={'display': 'none'}),

    dash_table.DataTable(
        id='object-table',
        columns=[
            {"name": "Object ID", "id": "ObjectID"},
            {"name": "Object Number", "id": "ObjectNumber"},
            {"name": "Object Name", "id": "ObjectName"},
            {"name": "Dated", "id": "Dated"},
            {"name": "Date Begin", "id": "DateBegin"},
            {"name": "Date End", "id": "DateEnd"},
            {"name": "Medium", "id": "Medium"},
            {"name": "Dimensions", "id": "Dimensions"},
            {"name": "Description", "id": "Description"},
            {"name": "Notes", "id": "Notes"},
            {"name": "Short Text", "id": "ShortText8"},
            {"name": "Bestandteil", "id": "Bestandteil"}
        ],
        page_size=20,
        sort_action='native',
        filter_action='native',
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': 'rgb(230, 230, 230)',
            'fontWeight': 'bold'
        },
        style_cell={
            'textAlign': 'left',
            'minWidth': '0px', 'maxWidth': '180px',
            'whiteSpace': 'normal'
        }
    )
])

# Specialized data exploration page layout
specialized_page_layout = html.Div([
    nav_bar,
    html.H1("Specialized Data Exploration"),
    
    html.H2("Color Distribution"),
    dcc.Graph(id='colors-chart')
])

# Main app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Callback for URL routing
@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/specialized':
        return specialized_page_layout
    else:
        return home_page_layout

# Home page callbacks
@app.callback(
    [Output('object-distribution-chart', 'figure'),
     Output('summary-stats', 'children'),
     Output('click-data', 'children'),
     Output('object-table', 'data')],
    [Input('category-dropdown', 'value'),
     Input('object-distribution-chart', 'clickData')]
)
def update_chart_and_summary(selected_categories, click_data):
    # Update charts based on dropdown selection
    filtered_data = medium_counts[medium_counts['Category'].isin(selected_categories)]
    
    if filtered_data.empty:
        fig = px.bar(title='No data available for selected categories')
        summary = html.Div([
            html.P("No object types found for the selected categories."),
            html.P("Please select different categories.")
        ])
        click_message = "No data"
        table_data = []
        return fig, summary, click_message, table_data
    
    fig = px.bar(filtered_data, 
                 x='Medium_Type', 
                 y='Count', 
                 color='Category',
                 labels={'Medium_Type': 'Object Type', 'Count': 'Frequency'},
                 title='Object Medium Distribution',
                 hover_data=['Medium_Type', 'Count', 'Category'])
    
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title='',
        yaxis_title='Frequency',
        legend_title='Object Category',
        height=600
    )
    
    fig.update_layout(
        updatemenus=[
            dict(
                type="buttons",
                direction="right",
                x=0.7,
                y=1.2,
                showactive=True,
                buttons=[
                    dict(label="Linear Scale",
                         method="relayout",
                         args=[{"yaxis.type": "linear"}]),
                    dict(label="Log Scale",
                         method="relayout",
                         args=[{"yaxis.type": "log"}])
                ]
            )
        ]
    )

    total_count = filtered_data['Count'].sum()
    most_common = filtered_data.loc[filtered_data['Count'].idxmax(), 'Medium_Type'] if not filtered_data.empty else "N/A"
    
    summary = html.Div([
        html.P(f"Total object instances: {total_count}"),
        html.P(f"Most common object type: {most_common}"),
        html.P(f"Number of object types: {len(filtered_data)}")
    ])

    # Handle click data for additional details
    click_message = "No data"
    table_data = []
    if click_data:
        clicked_object = click_data['points'][0]['x']
        click_message = f"You clicked on: {clicked_object}"
        details = medium_counts[medium_counts['Medium_Type'] == clicked_object]
        details_text = html.Div([
            html.P(f"Details for {clicked_object}:"),
            html.P(f"Count: {details['Count'].values[0]}"),
            html.P(f"Category: {details['Category'].values[0]}")
        ])
        
        # Populate the table with all related objects
        related_objects = objects_df[objects_df['Medium'].str.contains(clicked_object, case=False, na=False)]
        related_objects = related_objects.drop(columns=['SortNumber', 'Authority50ID', 'DateRemarks', 'DimensionRemarks'])
        table_data = related_objects.to_dict('records')
        
        return fig, details_text, click_message, table_data
    
    return fig, summary, click_message, table_data

# Specialized page callbacks
@app.callback(
    Output('colors-chart', 'figure'),
    [Input('url', 'pathname')]
)
def update_specialized_content(pathname):
    if pathname == '/specialized':
        # Create the color distribution chart
        color_fig = px.bar(color_counts, 
                           x='Color', 
                           y='Count', 
                           labels={'Color': 'Color', 'Count': 'Frequency'},
                           title='Distribution of Colors',
                           hover_data=['Color', 'Count'])

        color_fig.update_layout(
            xaxis_tickangle=-45,
            xaxis_title='',
            yaxis_title='Frequency',
            height=600
        )
        return color_fig
    return {}

if __name__ == '__main__':
    app.run_server(debug=True)
