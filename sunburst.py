import pandas as pd
import plotly.express as px

def load_sunburst_data(userfields_df):
    """Load and preprocess data for the sunburst chart."""
    from static_data import settings_columns

    # Consolidate data for sunburst chart
    sunburst_data = {
        'SettingType': [],
        'Component': [],
        'Attribute': [],
        'Value': [],
        'Count': []
    }

    def process_setting(setting_name, columns):
        available_columns = [col for col in columns if col in userfields_df.columns]
        df_setting = userfields_df[available_columns]
        for column in available_columns:
            value_counts = df_setting[column].value_counts()
            for value, count in value_counts.items():
                if not pd.isna(value):
                    sunburst_data['SettingType'].append(setting_name)
                    sunburst_data['Component'].append(column.split(':')[0])
                    sunburst_data['Attribute'].append(column)
                    sunburst_data['Value'].append(value)
                    sunburst_data['Count'].append(count)

    for setting, columns in settings_columns.items():
        process_setting(setting, columns)

    return pd.DataFrame(sunburst_data)

def create_sunburst_chart(df_sunburst, selected_path=None):
    """Create the sunburst chart."""
    fig = px.sunburst(
        df_sunburst,
        width=1800,
        height=1000,
        path=['SettingType', 'Component', 'Attribute', 'Value'],
        values='Count',
        color='SettingType',
        color_discrete_map={
            'Claw setting': '#FF6347',
            'Setting with three pearls': '#4682B4',
            'Bezel setting': '#32CD32',
            'Prong setting': '#9370DB',
            'Setting on the central cross': '#FF8C00',
            'Pearl setting': '#00CED1'
        },
        title='Hierarchical Structure of Settings'
    )

    fig.update_layout(
        margin=dict(t=100, l=20, r=350, b=20),
        uniformtext=dict(minsize=8, mode='hide'),
        showlegend=False,
        annotations=[
            dict(
                text="Hierarchy: Inner to Outer - Setting Type > Component > Attribute > Value",
                showarrow=False,
                x=0.5,
                y=1.06,
                xref='paper',
                yref='paper',
                font=dict(size=12)
            )
        ],
        paper_bgcolor='white',
        plot_bgcolor='white'
    )

    fig.update_traces(
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percentRoot:.2%}<extra></extra>',
        textfont=dict(size=10),
    )

    if selected_path:
        fig.update_traces(
            insidetextfont=dict(color='white', size=10),
            marker=dict(line=dict(color='black', width=2)),
            selector=dict(customdata=selected_path)
        )

    legend_items = [
        ('Claw setting', '#FF6347'),
        ('Setting with three pearls', '#4682B4'),
        ('Bezel setting', '#32CD32'),
        ('Prong setting', '#9370DB'),
        ('Setting on the central cross', '#FF8C00'),
        ('Pearl setting', '#00CED1')
    ]

    total_counts = df_sunburst.groupby('SettingType')['Count'].sum().reset_index()

    for i, (name, color) in enumerate(legend_items):
        fig.add_shape(
            type="rect",
            x0=1.02, y0=0.95 - i*0.08, x1=1.04, y1=0.96 - i*0.08,
            xref="paper", yref="paper",
            fillcolor=color,
            line_color=color,
        )
        fig.add_annotation(
            x=1.05, y=0.955 - i*0.08,
            xref="paper", yref="paper",
            text=name,
            showarrow=False,
            font=dict(size=12),
            xanchor="left",
            align="left",
        )
        count = total_counts[total_counts['SettingType'] == name]['Count'].values[0]
        fig.add_annotation(
            x=1.05, y=0.92 - i*0.08,
            xref="paper", yref="paper",
            text=f"Total: {count}",
            showarrow=False,
            font=dict(size=12),
            xanchor="left",
            align="left",
        )

    return fig
