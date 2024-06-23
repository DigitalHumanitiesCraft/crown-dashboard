import pandas as pd
import plotly.express as px

# Load the data
objects_df = pd.read_excel('data/CROWN_Objects_1_2024_02_02.xlsx')
userfields_df = pd.read_excel('data/crown-userfields.xlsx')

# Fill missing values with 'Unknown' for consistency
objects_df.fillna('Unknown', inplace=True)
userfields_df.fillna('Unknown', inplace=True)

# Filter for gemstone-related data in objects_df
gemstones_df = objects_df[objects_df['Medium'].str.contains('edelstein', na=False)]

# Define relevant user-defined fields for gemstones
gemstone_fields = [
    'Bohrloch: Anzahl', 'Bohrloch: Art', 'Bohrloch: Ausrichtung', 'Bohrloch: Bearbeitungsspuren',
    'Bohrloch: Durchmesser', 'Bohrloch: Sonstiges', 'Farbe', 'Form: Schliff',
    'Form: Schliff: Beschreibung', 'Form: Sonstiges', 'Form: Stein in Fassung', 'Oberfläche',
    'Schliffform: vor-/mittelalterlich: Wahrscheinlichkeit', 'Sonstige Beschreibung'
]

# Filter userfields_df to include only the relevant fields
filtered_userfields_df = userfields_df[['ID'] + [field for field in gemstone_fields if field in userfields_df.columns]]

# Merge the gemstone data with user-defined fields
merged_gemstone_data = pd.merge(gemstones_df, filtered_userfields_df, left_on='ObjectID', right_on='ID', how='left')

# Verify which fields are present in merged_gemstone_data
existing_fields = [field for field in gemstone_fields if field in merged_gemstone_data.columns]

# Drop rows where all relevant user-defined fields are NaN
merged_gemstone_data.dropna(subset=existing_fields, how='all', inplace=True)

# Check the first few rows of the merged data to ensure it looks correct
print(merged_gemstone_data.head())

# Create a scatter plot of the gemstones
fig = px.scatter(
    merged_gemstone_data,
    x='ObjectID',
    y='Medium',
    color='Medium',
    hover_data={
        'Form: Schliff': True,
        'Bohrloch: Anzahl': True,
        'Bohrloch: Durchmesser': True,
        'ObjectID': False
    },
    title='Gemstones Visualization'
)

# Show the plot
fig.show()

# Save the plot as an image (if kaleido is installed)
# fig.write_image("gemstones_visualization.png")
