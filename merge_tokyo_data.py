import pandas as pd

# Step 1: Load the datasets
original_df = pd.read_csv("athlete_events.csv")
athletes_2020 = pd.read_csv("athletes.csv")
medals_2020 = pd.read_csv("medals.csv")

# Step 2: Rename columns to prepare for merge
athletes_2020.rename(columns={
    'name': 'athlete',
    'country_code': 'NOC',
    'discipline': 'Sport',
    'gender': 'Sex',
    'height_m/ft': 'Height'
}, inplace=True)

medals_2020.rename(columns={
    'athlete_name': 'athlete',
    'medal_type': 'Medal',
    'country_code': 'NOC',
    'discipline': 'Sport'
}, inplace=True)

# Step 3: Merge on athlete + sport + NOC
tokyo_df = pd.merge(
    athletes_2020,
    medals_2020[['athlete', 'Sport', 'NOC', 'Medal']],
    how='left',
    on=['athlete', 'Sport', 'NOC']
)

# Step 4: Add fixed columns for Tokyo 2020
tokyo_df['Games'] = '2020 Summer'
tokyo_df['Year'] = 2020
tokyo_df['Season'] = 'Summer'
tokyo_df['City'] = 'Tokyo'
tokyo_df['Age'] = None  # Not available
tokyo_df['Weight'] = None  # Not available
tokyo_df['Team'] = tokyo_df['country']  # fallback for Team
tokyo_df['Event'] = None  # Not available in athletes.csv

# Step 5: Rename columns to match athlete_events.csv
tokyo_df.rename(columns={
    'athlete': 'Name',
}, inplace=True)

# Step 6: Reorder and align all required columns
expected_cols = ['Name', 'Sex', 'Age', 'Height', 'Weight', 'Team', 'NOC',
                 'Games', 'Year', 'Season', 'City', 'Sport', 'Event', 'Medal']

for col in expected_cols:
    if col not in tokyo_df.columns:
        tokyo_df[col] = None

tokyo_df = tokyo_df[expected_cols]

# Ensure NOC exists and is in uppercase
tokyo_df['NOC'] = tokyo_df['NOC'].fillna(tokyo_df['Team'])  # fallback if NOC is missing
tokyo_df['NOC'] = tokyo_df['NOC'].str.upper()

# Step 7: Concatenate with original dataset
updated_df = pd.concat([original_df, tokyo_df], ignore_index=True)
updated_df.to_csv("athlete_events_updated.csv", index=False)

print(" Merge complete. File saved as athlete_events_updated.csv")
