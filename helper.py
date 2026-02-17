import numpy as np

def fetch_medal_tally(df, year, country):
    temp_df = df.dropna(subset=['Medal'])

    if year != "Overall":
        temp_df = temp_df[temp_df['Year'] == int(year)]
    if country != "Overall":
        temp_df = temp_df[temp_df['region'] == country]

    medal_tally = temp_df.groupby(['region', 'Medal']).size().unstack(fill_value=0)

    for col in ['Gold', 'Silver', 'Bronze']:
        if col not in medal_tally.columns:
            medal_tally[col] = 0

    medal_tally = medal_tally[['Gold', 'Silver', 'Bronze']].sort_values("Gold", ascending=False).reset_index()
    medal_tally['total'] = medal_tally['Gold'] + medal_tally['Silver'] + medal_tally['Bronze']

    return medal_tally.astype({'Gold': 'int', 'Silver': 'int', 'Bronze': 'int', 'total': 'int'})


def country_year_list(df):
    years = df['Year'].unique().tolist()
    years.sort()
    years.insert(0, 'Overall')

    country = np.unique(df['region'].dropna().values).tolist()
    country.sort()
    country.insert(0, 'Overall')

    return years, country


def data_over_time(df, col):
    nations_over_time = df.drop_duplicates(['Year', col])['Year'].value_counts().reset_index()
    nations_over_time.columns = ['Edition', col]
    nations_over_time = nations_over_time.sort_values('Edition')
    return nations_over_time


def most_successful(df, sport):
    temp_df = df.dropna(subset=['Medal'])

    if sport != 'Overall':
        temp_df = temp_df[temp_df['Sport'] == sport]

    top_athletes = temp_df['Name'].value_counts().reset_index().head(15)
    top_athletes.columns = ['Name', 'Medals']

    merged_df = top_athletes.merge(df, on='Name', how='left')[['Name', 'Medals', 'Sport', 'region']]
    merged_df = merged_df.drop_duplicates('Name')

    return merged_df


def yearwise_medal_tally(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]
    final_df = new_df.groupby('Year').count()['Medal'].reset_index()

    return final_df


def country_event_heatmap(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df.drop_duplicates(subset=['Team', 'NOC', 'Games', 'Year', 'City', 'Sport', 'Event', 'Medal'], inplace=True)

    new_df = temp_df[temp_df['region'] == country]

    pt = new_df.pivot_table(index='Sport', columns='Year', values='Medal', aggfunc='count').fillna(0)
    return pt


def most_successful_countrywise(df, country):
    temp_df = df.dropna(subset=['Medal'])
    temp_df = temp_df[temp_df['region'] == country]

    top_athletes = temp_df['Name'].value_counts().reset_index().head(10)
    top_athletes.columns = ['Name', 'Medals']

    merged_df = top_athletes.merge(df, on='Name', how='left')[['Name', 'Medals', 'Sport']]
    merged_df = merged_df.drop_duplicates('Name')

    return merged_df


def weight_v_height(df, sport):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])
    athlete_df['Medal'].fillna('No Medal', inplace=True)
    if sport != 'Overall':
        return athlete_df[athlete_df['Sport'] == sport]
    return athlete_df


def men_vs_women(df):
    athlete_df = df.drop_duplicates(subset=['Name', 'region'])

    men = athlete_df[athlete_df['Sex'] == 'M'].groupby('Year').count()['Name'].reset_index()
    women = athlete_df[athlete_df['Sex'] == 'F'].groupby('Year').count()['Name'].reset_index()

    final = men.merge(women, on='Year', how='left')
    final.rename(columns={'Name_x': 'Male', 'Name_y': 'Female'}, inplace=True)
    final.fillna(0, inplace=True)

    return final
