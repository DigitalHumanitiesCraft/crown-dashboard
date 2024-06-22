import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from urllib.parse import quote as url_quote

# Import static data
from static_data import color_mapping, color_columns, damage_columns, table_columns, unique_categories

def load_data():
    """Load data from Excel files."""
    objects_df = pd.read_excel('data/CROWN_Objects_1_2024_02_02.xlsx')
    userfields_df = pd.read_excel('data/crown-userfields.xlsx')
    return objects_df, userfields_df

def preprocess_data(objects_df, userfields_df):
    """Preprocess data for use in the dashboard."""
    def process_medium_types(medium_string):
        if pd.isna(medium_string):
            return []
        return [m.strip() for m in medium_string.split(';') if m.strip()]

    medium_types = objects_df['Medium'].apply(process_medium_types).explode()
    medium_counts = medium_types.value_counts().reset_index()
    medium_counts.columns = ['Medium_Type', 'Count']

    unique_mediums = medium_counts['Medium_Type'].unique()
    unique_categories = {um.strip().lower(): um.strip().capitalize() for um in unique_mediums}

    def categorize_medium(medium_type):
        medium_list = medium_type.split(';')
        categorized_list = []
        for medium in medium_list:
            medium_cleaned = medium.strip().lower()
            categorized_list.append(unique_categories.get(medium_cleaned, 'Other'))
        return '; '.join(categorized_list)

    medium_counts['Category'] = medium_counts['Medium_Type'].apply(categorize_medium)

    color_data = userfields_df[color_columns]
    color_counts_presence = color_data.apply(lambda col: col.isin([1, '1', 1.0, '1.0']).sum()).reset_index()
    color_counts_presence.columns = ['Enamel Color', 'Count']
    color_counts_presence = color_counts_presence[color_counts_presence['Count'] > 0]
    color_counts_presence = color_counts_presence.sort_values(by='Count', ascending=False)

    merged_data = pd.merge(objects_df, userfields_df, left_on='ObjectID', right_on='ID', how='inner')
    relevant_columns_with_bestandteil = damage_columns + ['Bestandteil']
    filtered_data_with_bestandteil = merged_data[relevant_columns_with_bestandteil]

    damage_counts_by_bestandteil = filtered_data_with_bestandteil.groupby('Bestandteil').apply(
        lambda df: df.drop(columns=['Bestandteil']).notna().sum()
    ).reset_index()
    
    damage_counts_by_bestandteil.columns = ['Bestandteil'] + damage_counts_by_bestandteil.columns[1:].tolist()
    filtered_damage_counts = damage_counts_by_bestandteil.loc[
        ~(damage_counts_by_bestandteil.drop(columns=['Bestandteil']) == 0).all(axis=1)
    ]

    return medium_counts, color_counts_presence, color_columns, filtered_damage_counts

def get_related_objects_by_ids(objects_df, related_ids):
    """Filter objects_df based on related IDs and format for DataTable."""
    related_objects = objects_df[objects_df['ObjectID'].isin(related_ids)]
    related_objects = related_objects.drop(columns=['SortNumber', 'Authority50ID', 'DateRemarks', 'DimensionRemarks'], errors='ignore')
    
    related_objects = related_objects[table_columns]
    return related_objects.to_dict('records')

# Load and preprocess the data
objects_df, userfields_df = load_data()
medium_counts, color_counts_presence, color_columns, filtered_damage_counts = preprocess_data(objects_df, userfields_df)

# Layout Definitions

# Define the navigation bar
nav_bar = html.Div([
    dcc.Link('Home', href='/', className='nav-link'),
    dcc.Link('Enamel Color Distribution', href='/colors', className='nav-link'),
    dcc.Link('Enamel Damage Distribution', href='/damage', className='nav-link') 
], className='nav-bar')

# Home page layout
def create_home_page_layout():
    return html.Div([
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
            columns=[{"name": col, "id": col} for col in table_columns],
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

# Enamel Damage Distribution page layout
def create_damage_distribution_layout():
    return html.Div([
        nav_bar,
        html.H1("Enamel Damage Distribution"),
        
        dcc.Graph(id='damage-distribution-chart'),  # Placeholder for the stacked bar chart

        html.Div(id='click-data-damage', style={'display': 'none'}),

        dash_table.DataTable(
            id='damage-object-table',
            columns=[{"name": col, "id": col} for col in table_columns],
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

# Enamel Color Distribution page layout
def create_color_distribution_layout():
    return html.Div([
        nav_bar,
        html.H1("Enamel Color Distribution"),
        
        dcc.Graph(id='enamel-colors-chart'),
        html.Div(id='click-data-color', style={'display': 'none'}),
        
        dash_table.DataTable(
            id='color-object-table',
            columns=[{"name": col, "id": col} for col in table_columns],
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

# Define Callbacks

def register_callbacks(app):
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname')]
    )
    def display_page(pathname):
        if pathname == '/colors':
            return create_color_distribution_layout()
        elif pathname == '/damage':
            return create_damage_distribution_layout()
        else:
            return create_home_page_layout()

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
            table_data = get_related_objects_by_ids(objects_df, related_objects['ObjectID'])
            
            return fig, details_text, click_message, table_data
        
        return fig, summary, click_message, table_data

    # Define the color mapping
    color_mapping = {
        'opak blau (obla)': '#0000FF',
        'opak gelb (ogel)': '#FFFF00',
        'opak grün (ogru)': '#00FF00',
        'opak hellblau (ohbl)': '#ADD8E6',
        'opak inkarnat (oink)': '#FFC0CB',
        'opak rot (orot)': '#FF0000',
        'opak türkis (otue)': '#40E0D0',
        'opak weiß (owei)': '#FFFFFF',
        '(semi)transparent dunkelblau (tdbl)': '#00008B',
        'transparent blau (tbla)': '#0000FF',
        'transparent braun (tbra)': '#A52A2A',
        'transparent grün (tgru)': '#00FF00',
        'transparent hellgrün (thgr)': '#90EE90',
        'transparent dunkelgrün (tdgr)': '#006400',
        'transparent schwarz (tsch)': '#000000',
        'transparent türkis (ttue)': '#40E0D0'
    }

    @app.callback(
        [Output('enamel-colors-chart', 'figure'),
         Output('color-object-table', 'data')],
        [Input('url', 'pathname'),
         Input('enamel-colors-chart', 'clickData')]
    )
    def update_enamel_colors_chart(pathname, click_data):
        if pathname == '/colors':
            # Apply color mapping
            colors = [color_mapping.get(color, '#808080') for color in color_counts_presence['Enamel Color']]
            
            fig = px.bar(color_counts_presence, 
                         x='Enamel Color', 
                         y='Count', 
                         labels={'Enamel Color': 'Enamel Color', 'Count': 'Frequency'}, 
                         title='Distribution of Enamel Colors',
                         color=color_counts_presence['Enamel Color'],  # Use colors from the mapping
                         color_discrete_map=color_mapping)

            fig.update_layout(
                xaxis_tickangle=-45,
                xaxis_title='Enamel Color',
                yaxis_title='Count',
                height=600
            )

            table_data = []
            if click_data:
                clicked_color = click_data['points'][0]['x']
                color_column = next(col for col in color_columns if clicked_color in col)
                related_ids = userfields_df[userfields_df[color_column].isin([1, '1', 1.0, '1.0'])]['ID']
                table_data = get_related_objects_by_ids(objects_df, related_ids)

            return fig, table_data
        return {}, []

    # Damage Distribution Chart Callback
    @app.callback(
        [Output('damage-distribution-chart', 'figure'),
         Output('damage-object-table', 'data')],
        [Input('url', 'pathname'),
         Input('damage-distribution-chart', 'clickData')]
    )
    def update_damage_distribution_chart(pathname, click_data):
        if pathname == '/damage':
            fig = px.bar(
                filtered_damage_counts,
                x='Bestandteil',
                y=filtered_damage_counts.columns[1:],
                title='Damage Conditions by Component',
                labels={'value': 'Count', 'variable': 'Damage Condition'}
            )
            fig.update_layout(barmode='stack', xaxis_tickangle=-45)

            table_data = []
            if click_data:
                clicked_damage = click_data['points'][0]['x']
                print(f"Clicked damage: {clicked_damage}")  # Debug print statement
                try:
                    damage_column = next(col for col in filtered_damage_counts.columns[1:] if clicked_damage in col)
                    related_ids = userfields_df[userfields_df[damage_column].notna()]['ID']
                    table_data = get_related_objects_by_ids(objects_df, related_ids)
                except StopIteration:
                    print(f"No matching column found for clicked damage: {clicked_damage}")

            return fig, table_data

        return go.Figure(), []

# Main App Initialization

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose the Flask server

# Define the main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)



