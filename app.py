import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output
from dash.dash_table.Format import Format, Scheme
import plotly.express as px
from urllib.parse import quote as url_quote
import pandas as pd

# Import static data
from static_data import color_mapping, color_columns, damage_columns, table_columns, unique_categories
from sunburst import create_sunburst_chart, load_sunburst_data

columns = [{"name": col, "id": col} for col in table_columns]
columns.append({"name": "FileName_paths", "id": "FileName_paths", "presentation": "markdown"})


# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server  # Expose the Flask server

def load_data():
    """Load data from Excel files."""
    objects_df = pd.read_excel('data/CROWN_Objects_1_2024_02_02.xlsx')
    userfields_df = pd.read_excel('data/crown-userfields.xlsx')
    restaurierung_1_df = pd.read_excel('data/CROWN_Restaurierung_1_2024_02_02.xlsx')
    restaurierung_2_df = pd.read_excel('data/CROWN_Restaurierung_2_2024_02_02.xlsx')
    paths_df = pd.read_excel('data/CROWN_Restaurierung_3_Medien_2024_02_02.xlsx')
    return objects_df, userfields_df, restaurierung_1_df, restaurierung_2_df, paths_df

def preprocess_data(objects_df, userfields_df, restaurierung_1_df, restaurierung_2_df, paths_df):
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

    # Use include_groups=False to silence the deprecation warning
    damage_counts_by_bestandteil = filtered_data_with_bestandteil.groupby('Bestandteil', group_keys=False).apply(
        lambda df: df.loc[:, df.columns != 'Bestandteil'].notna().sum()
    ).reset_index()

    damage_counts_by_bestandteil.columns = ['Bestandteil'] + damage_counts_by_bestandteil.columns[1:].tolist()
    filtered_damage_counts = damage_counts_by_bestandteil.loc[
        ~(damage_counts_by_bestandteil.drop(columns=['Bestandteil']) == 0).all(axis=1)
    ]

    # Ensure unique column names before merging
    restaurierung_2_df = restaurierung_2_df.add_suffix('_rest2')
    paths_df = paths_df.add_suffix('_paths')
    restaurierung_1_df = restaurierung_1_df.add_suffix('_rest1')
    
    # Merge paths with objects step by step
    merged_df1 = pd.merge(restaurierung_2_df, paths_df[['CondLineItemID_paths', 'FileName_paths']], left_on='CondLineItemID_rest2', right_on='CondLineItemID_paths', how='left')
    merged_df2 = pd.merge(restaurierung_1_df, merged_df1, left_on='ConditionID_rest1', right_on='ConditionID_rest2', how='left')
    merged_with_paths = pd.merge(objects_df, merged_df2, left_on='ObjectID', right_on='ID_rest1', how='left')
    
    # Handle duplicated ObjectNumber columns
    if 'ObjectNumber_rest1' in merged_with_paths.columns and 'ObjectNumber' in merged_with_paths.columns:
        merged_with_paths['ObjectNumber'] = merged_with_paths['ObjectNumber'].combine_first(merged_with_paths['ObjectNumber_rest1'])
        merged_with_paths = merged_with_paths.drop(columns=['ObjectNumber_rest1'])
    
    # Check columns after merge to ensure 'FileName_paths' is included
    if 'FileName_paths' not in merged_with_paths.columns:
        print("FileName column is missing after merge. Available columns:", merged_with_paths.columns)
    else:
        print("FileName column successfully merged.")
    
    return medium_counts, color_counts_presence, color_columns, filtered_damage_counts, merged_with_paths

def get_related_objects_by_ids(objects_df, related_ids):
    """Filter objects_df based on related IDs and format for DataTable."""
    related_objects = objects_df[objects_df['ObjectID'].isin(related_ids)]
    related_objects = related_objects.drop(columns=['SortNumber', 'Authority50ID', 'DateRemarks', 'DimensionRemarks'], errors='ignore')

    # Check if 'FileName_paths' is present before attempting to use it
    if 'FileName_paths' not in related_objects.columns:
        print("FileName column is missing. Available columns:", related_objects.columns)
        return related_objects[table_columns + ['ObjectNumber']].to_dict('records')
    else:
        # Apply the hyperlink formatting
        related_objects = format_filename_as_link(related_objects)
        return related_objects[table_columns + ['ObjectNumber', 'FileName_paths']].to_dict('records')

# Load and preprocess data
objects_df, userfields_df, restaurierung_1_df, restaurierung_2_df, paths_df = load_data()
medium_counts, color_counts_presence, color_columns, filtered_damage_counts, merged_with_paths = preprocess_data(objects_df, userfields_df, restaurierung_1_df, restaurierung_2_df, paths_df)

# Layout Definitions

def format_filename_as_link(df):
    """Format the FileName_paths column as clickable download links."""
    zenodo_base_url = "https://zenodo.org/api/records/12508052/files/"
    
    def create_download_link(file_path):
        # Extract the filename from the full path
        file_name = file_path.split("\\")[-1]
        # URL encode the filename
        encoded_file_name = url_quote(file_name)
        # Create the download URL
        download_url = f"{zenodo_base_url}{encoded_file_name}/content"
        return f'[Download]({download_url})'
    
    df['FileName_paths'] = df['FileName_paths'].apply(
        lambda x: create_download_link(x) if pd.notna(x) else ""
    )
    return df

# Define the navigation bar
nav_bar = html.Div([
    dcc.Link('Home', href='/', className='nav-link'),
    dcc.Link('Enamel Color Distribution', href='/colors', className='nav-link'),
    dcc.Link('Enamel Damage Distribution', href='/damage', className='nav-link'),
    dcc.Link('Sunburst Chart', href='/sunburst', className='nav-link')
], className='nav-bar')

# Home
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
            columns=columns,
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

# Enamel Damage Distribution
def create_damage_distribution_layout():
    return html.Div([
        nav_bar,
        html.H1("Enamel Damage Distribution"),
        dcc.Graph(id='damage-distribution-chart'),
        html.Div(id='click-data-damage', style={'display': 'none'}),
        dash_table.DataTable(
            id='damage-object-table',
            columns=columns,
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

# Enamel Color Distribution
def create_color_distribution_layout():
    return html.Div([
        nav_bar,
        html.H1("Enamel Color Distribution"),
        dcc.Graph(id='enamel-colors-chart'),
        html.Div(id='click-data-color', style={'display': 'none'}),
        dash_table.DataTable(
            id='color-object-table',
            columns=columns,
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

# Settings Sunburst
def create_sunburst_layout():
    return html.Div([
        nav_bar,
        html.H1("Settings"),
        dcc.Graph(id='sunburst-chart'),
        dash_table.DataTable(
            id='sunburst-table',
            columns=[{"name": col, "id": col} for col in ['ObjectID', 'ObjectNumber', 'ObjectName', 'DateBegin', 'DateEnd', 'Medium', 'Description', 'Notes']],
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
        elif pathname == '/sunburst':
            return create_sunburst_layout()
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
            table_data = get_related_objects_by_ids(merged_with_paths, related_objects['ObjectID'])
            
            return fig, details_text, click_message, table_data
        
        return fig, summary, click_message, table_data

    @app.callback(
        [Output('enamel-colors-chart', 'figure'),
         Output('color-object-table', 'data')],
        [Input('url', 'pathname'),
         Input('enamel-colors-chart', 'clickData')]
    )
    def update_enamel_colors_chart(pathname, click_data):
        if pathname == '/colors':
            fig = px.bar(color_counts_presence, 
                         x='Enamel Color', 
                         y='Count', 
                         labels={'Enamel Color': 'Enamel Color', 'Count': 'Frequency'}, 
                         title='Distribution of Enamel Colors',
                         color=color_counts_presence['Enamel Color'],
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
                table_data = get_related_objects_by_ids(merged_with_paths, related_ids)

                if 'FileName_paths' not in merged_with_paths.columns:
                    print("FileName_paths column is missing in merged_with_paths. Available columns:", merged_with_paths.columns)

            return fig, table_data
        return {}, []

    @app.callback(
        [Output('sunburst-chart', 'figure'),
         Output('sunburst-table', 'data')],
        [Input('sunburst-chart', 'clickData')]
    )
    def update_sunburst_chart(click_data):
        df_sunburst = load_sunburst_data(userfields_df)
        selected_path = None
        
        if click_data:
            selected_value = click_data['points'][0]['label']
            selected_path = click_data['points'][0]['id'].split('/')
            related_objects = userfields_df[userfields_df.apply(lambda row: selected_value in row.values, axis=1)]
            related_object_ids = related_objects['ID'].unique()
            filtered_objects = merged_with_paths[merged_with_paths['ObjectID'].isin(related_object_ids)]
            table_data = filtered_objects.to_dict('records')
        else:
            table_data = []

        fig = create_sunburst_chart(df_sunburst, selected_path)
        return fig, table_data

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
                print(f"Click data: {click_data}")  # Debug print statement
                clicked_index = click_data['points'][0]['pointIndex']
                clicked_bestandteil = filtered_damage_counts.iloc[clicked_index]['Bestandteil']
                print(f"Clicked Bestandteil: {clicked_bestandteil}")  # Debug print statement

                for damage_type in damage_columns:
                    if filtered_damage_counts.at[clicked_index, damage_type] > 0:
                        print(f"Matching damage type: {damage_type}")  # Debug print statement
                        related_ids = userfields_df[userfields_df[damage_type].notna()]['ID']
                        table_data = get_related_objects_by_ids(merged_with_paths, related_ids)
                        break

            return fig, table_data

        return go.Figure(), []

# Main App Initialization

# Initialize the Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# Define the main layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

# Register callbacks
register_callbacks(app)

if __name__ == '__main__':
    app.run_server(debug=True)




