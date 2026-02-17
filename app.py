import streamlit as st
import pandas as pd
import preprocessor
import helper
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import os
from pathlib import Path

# Page Configuration
st.set_page_config(
    page_title="Olympic Explorer",
    page_icon="🏅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Background Styling
def add_bg_from_local(image_file):
    """Add background image to the app"""
    try:
        if os.path.exists(image_file):
            with open(image_file, "rb") as image:
                encoded = base64.b64encode(image.read()).decode()
            css = f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpg;base64,{encoded}");
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-opacity: 0.1;
            }}
            .main .block-container {{
                background-color: rgba(255, 255, 255, 0.95);
                padding: 2rem;
                border-radius: 10px;
            }}
            </style>
            """
            st.markdown(css, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load background image: {e}")

# Helper function to load flag image
def load_flag_image(country_name):
    """Load country flag image if available"""
    flag_path = f"flags/{country_name}.png"
    if os.path.exists(flag_path):
        return flag_path
    return None

# Data Loading with Caching
@st.cache_data
def load_data():
    """Load and preprocess data with caching for performance"""
    try:
        df = pd.read_csv("athlete_events_updated.csv")
        region_df = pd.read_csv("noc_regions.csv")
        df = preprocessor.preprocess(df, region_df)
        return df, region_df
    except FileNotFoundError as e:
        st.error(f"Data file not found: {e}")
        st.stop()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.stop()

# Load data
with st.spinner("Loading Olympic data..."):
    df, region_df = load_data()

# Sidebar Navigation
st.sidebar.title("🏅 Olympic Explorer")
st.sidebar.markdown("---")

# Try to load sidebar image
sidebar_image_path = "Gemini_Generated_Image_gswhsagswhsagswh.png"
if os.path.exists(sidebar_image_path):
    st.sidebar.image(sidebar_image_path, use_container_width=True)
else:
    st.sidebar.markdown("### Explore Olympic History")

# Add background image (optional - uncomment if you want it)
# add_bg_from_local("Bgimage.jpg")

user_menu = st.sidebar.radio(
    'Navigate through:',
    ('🏆 Medal Tally', '📈 Overall Analysis', '🌍 Country Insights', '🧍 Athlete Profile')
)

st.sidebar.markdown("---")

# Medal Tally
if user_menu == '🏆 Medal Tally':
    st.header("🏅 Medal Tally")
    
    try:
        years, country = helper.country_year_list(df)
        
        selected_year = st.sidebar.selectbox("Select Year", years)
        selected_country = st.sidebar.selectbox("Select Country", country)
        
        # Display flag
        flag_path = load_flag_image(selected_country)
        if flag_path:
            st.sidebar.image(flag_path, width=150, caption=f"Flag of {selected_country}")
        else:
            st.sidebar.markdown(f"🌍 **{selected_country}**")
        
        # Fetch medal tally
        medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)
        
        # Dynamic header
        if selected_year == 'Overall' and selected_country == 'Overall':
            st.subheader("Overall Medal Tally")
        elif selected_year != 'Overall' and selected_country == 'Overall':
            st.subheader(f"Medal Tally in {selected_year} Olympics")
        elif selected_year == 'Overall' and selected_country != 'Overall':
            st.subheader(f"{selected_country}'s Overall Performance")
        else:
            st.subheader(f"{selected_country}'s Performance in {selected_year} Olympics")
        
        # Display medal tally with better styling
        if not medal_tally.empty:
            # Add medal visualization
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.dataframe(
                    medal_tally.style.format({
                        'Gold': '{:d}',
                        'Silver': '{:d}',
                        'Bronze': '{:d}',
                        'total': '{:d}'
                    }).background_gradient(subset=['Gold', 'Silver', 'Bronze', 'total'], cmap='YlOrRd'),
                    use_container_width=True,
                    height=400
                )
            
            with col2:
                if len(medal_tally) > 0:
                    top_country = medal_tally.iloc[0]
                    st.metric("🥇 Top Country", top_country['region'])
                    st.metric("Total Medals", int(top_country['total']))
                    st.markdown(f"**Gold:** {int(top_country['Gold'])} | **Silver:** {int(top_country['Silver'])} | **Bronze:** {int(top_country['Bronze'])}")
            
            # Medal distribution chart
            if len(medal_tally) > 0:
                st.subheader("📊 Medal Distribution (Top 10 Countries)")
                top_10 = medal_tally.head(10)
                fig = px.bar(
                    top_10,
                    x='region',
                    y=['Gold', 'Silver', 'Bronze'],
                    title="Medal Distribution",
                    labels={'value': 'Number of Medals', 'region': 'Country'},
                    barmode='stack',
                    color_discrete_map={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
                )
                fig.update_layout(height=500, xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No medal data available for the selected filters.")
        
        # 2020 Olympics data section
        st.subheader("🏅 Tokyo 2020 Olympics - Medal Count by Region")
        try:
            test_df = df[(df['Year'] == 2020) & (df['Medal'].notnull())]
            if not test_df.empty:
                grouped = test_df.groupby(['region', 'Medal']).size().unstack(fill_value=0)
                grouped['Total'] = grouped.sum(axis=1)
                grouped = grouped.sort_values('Total', ascending=False)
                st.dataframe(grouped, use_container_width=True)
            else:
                st.info("No data available for 2020 Olympics.")
        except Exception as e:
            st.warning(f"Could not load 2020 data: {e}")
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please try selecting different filters.")

# Overall Analysis
elif user_menu == '📈 Overall Analysis':
    st.header("📊 Olympic Trends & Statistics")
    
    # Key Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        editions = df['Year'].nunique()
        st.metric("Editions", editions, help="Number of Olympic editions in the dataset")
    with col2:
        hosts = df['City'].nunique()
        st.metric("Host Cities", hosts, help="Number of unique host cities")
    with col3:
        sports = df['Sport'].nunique()
        st.metric("Sports", sports, help="Number of different sports")

    col4, col5, col6 = st.columns(3)
    with col4:
        events = df['Event'].nunique()
        st.metric("Events", events, help="Total number of unique events")
    with col5:
        nations = df['region'].nunique()
        st.metric("Nations", nations, help="Number of participating countries/regions")
    with col6:
        athletes = df['Name'].nunique()
        st.metric("Athletes", f"{athletes:,}", help="Total number of unique athletes")
    
    st.markdown("---")
    
    # Trends Over Time
    st.subheader("📈 Trends Over Time")
    
    try:
        # Participating Nations
        nations_data = helper.data_over_time(df, 'region')
        if not nations_data.empty:
            fig_nations = px.line(
                nations_data, 
                x="Edition", 
                y="region",
                title="Participating Nations Over Years",
                labels={'region': 'Number of Nations', 'Edition': 'Olympic Edition'},
                markers=True
            )
            fig_nations.update_traces(line_color='#1f77b4', line_width=3)
            fig_nations.update_layout(height=400)
            st.plotly_chart(fig_nations, use_container_width=True)
        
        # Events Over Time
        events_data = helper.data_over_time(df, 'Event')
        if not events_data.empty:
            fig_events = px.line(
                events_data, 
                x="Edition", 
                y="Event",
                title="Events Over Time",
                labels={'Event': 'Number of Events', 'Edition': 'Olympic Edition'},
                markers=True
            )
            fig_events.update_traces(line_color='#ff7f0e', line_width=3)
            fig_events.update_layout(height=400)
            st.plotly_chart(fig_events, use_container_width=True)
        
        # Athletes Over Time
        athletes_data = helper.data_over_time(df, 'Name')
        if not athletes_data.empty:
            fig_athletes = px.line(
                athletes_data, 
                x="Edition", 
                y="Name",
                title="Athletes Over Time",
                labels={'Name': 'Number of Athletes', 'Edition': 'Olympic Edition'},
                markers=True
            )
            fig_athletes.update_traces(line_color='#2ca02c', line_width=3)
            fig_athletes.update_layout(height=400)
            st.plotly_chart(fig_athletes, use_container_width=True)
    except Exception as e:
        st.warning(f"Error displaying trends: {e}")
    
    st.markdown("---")
    
    # Event Distribution Heatmap
    st.subheader("🔥 Event Distribution by Sport Over Years")
    try:
        event_heatmap = df.drop_duplicates(['Year', 'Sport', 'Event'])
        pivot_data = event_heatmap.pivot_table(
            index='Sport', 
            columns='Year', 
            values='Event', 
            aggfunc='count'
        ).fillna(0).astype(int)
        
        if not pivot_data.empty:
            fig, ax = plt.subplots(figsize=(16, 12))
            sns.heatmap(
                pivot_data,
                annot=True,
                fmt='d',
                linewidths=0.5,
                cmap="YlGnBu",
                cbar_kws={'label': 'Number of Events'},
                ax=ax
            )
            ax.set_title("Event Distribution by Sport and Year", fontsize=16, pad=20)
            ax.set_xlabel("Year", fontsize=12)
            ax.set_ylabel("Sport", fontsize=12)
            plt.xticks(rotation=45)
            plt.yticks(rotation=0)
            st.pyplot(fig)
        else:
            st.info("No data available for the heatmap.")
    except Exception as e:
        st.warning(f"Error creating heatmap: {e}")
    
    st.markdown("---")
    
    # Top Performing Athletes
    st.subheader("🏆 Top Performing Athletes")
    try:
        sport_list = sorted(df['Sport'].dropna().unique().tolist())
        sport_list.insert(0, 'Overall')
        selected_sport = st.selectbox('Select a Sport', sport_list, key='sport_select')
        
        top_athletes = helper.most_successful(df, selected_sport)
        if not top_athletes.empty:
            st.dataframe(
                top_athletes.style.format({'Medals': '{:d}'}),
                use_container_width=True,
                height=400
            )
        else:
            st.info("No athlete data available for the selected sport.")
    except Exception as e:
        st.warning(f"Error loading athlete data: {e}")

# Country Insights
elif user_menu == '🌍 Country Insights':
    st.header("🌍 Country-wise Performance Analysis")
    
    try:
        country_list = sorted(df['region'].dropna().unique().tolist())
        selected_country = st.sidebar.selectbox("Choose Country", country_list)
        
        # Display flag
        flag_path = load_flag_image(selected_country)
        if flag_path:
            st.sidebar.image(flag_path, width=150, caption=f"Flag of {selected_country}")
        else:
            st.sidebar.markdown(f"🌍 **{selected_country}**")
        
        # Country statistics
        country_data = df[df['region'] == selected_country]
        if not country_data.empty:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                total_medals = country_data['Medal'].notna().sum()
                st.metric("Total Medals", total_medals)
            with col2:
                gold_medals = (country_data['Medal'] == 'Gold').sum()
                st.metric("🥇 Gold", gold_medals)
            with col3:
                silver_medals = (country_data['Medal'] == 'Silver').sum()
                st.metric("🥈 Silver", silver_medals)
            with col4:
                bronze_medals = (country_data['Medal'] == 'Bronze').sum()
                st.metric("🥉 Bronze", bronze_medals)
        
        st.markdown("---")
        
        # Medal Tally Over Years
        st.subheader(f"{selected_country} - Medal Tally Over Years")
        try:
            country_df = helper.yearwise_medal_tally(df, selected_country)
            if not country_df.empty:
                fig = px.line(
                    country_df, 
                    x="Year", 
                    y="Medal",
                    title=f"{selected_country}'s Medal Count Over Years",
                    labels={'Medal': 'Number of Medals', 'Year': 'Year'},
                    markers=True
                )
                fig.update_traces(line_color='#FFD700', line_width=3, marker_size=8)
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No medal data available for {selected_country}.")
        except Exception as e:
            st.warning(f"Error displaying medal tally: {e}")
        
        # Top Sports Heatmap
        st.subheader(f"{selected_country}'s Performance by Sport Over Years")
        try:
            heatmap_data = helper.country_event_heatmap(df, selected_country)
            if not heatmap_data.empty:
                fig, ax = plt.subplots(figsize=(16, 10))
                sns.heatmap(
                    heatmap_data, 
                    annot=True, 
                    fmt='g',
                    cmap="crest",
                    cbar_kws={'label': 'Number of Medals'},
                    ax=ax
                )
                ax.set_title(f"{selected_country}'s Medal Performance by Sport and Year", fontsize=14, pad=20)
                ax.set_xlabel("Year", fontsize=12)
                ax.set_ylabel("Sport", fontsize=12)
                plt.xticks(rotation=45)
                plt.yticks(rotation=0)
                st.pyplot(fig)
            else:
                st.info(f"No heatmap data available for {selected_country}.")
        except Exception as e:
            st.warning(f"Error creating heatmap: {e}")
        
        st.markdown("---")
        
        # Top Athletes
        st.subheader(f"🏆 Top 10 Athletes from {selected_country}")
        try:
            top_athletes = helper.most_successful_countrywise(df, selected_country)
            if not top_athletes.empty:
                st.dataframe(
                    top_athletes.style.format({'Medals': '{:d}'}),
                    use_container_width=True,
                    height=400
                )
            else:
                st.info(f"No athlete data available for {selected_country}.")
        except Exception as e:
            st.warning(f"Error loading athlete data: {e}")
    
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Athlete Profile
elif user_menu == '🧍 Athlete Profile':
    st.header("🧍 Individual Athlete Insights")
    
    try:
        athlete_df = df.drop_duplicates(subset=['Name', 'region'])
        athlete_names = sorted(athlete_df['Name'].dropna().unique())
        
        if not athlete_names:
            st.warning("No athlete data available.")
        else:
            selected_athlete = st.selectbox("Select an Athlete", athlete_names)
            athlete_data = df[df['Name'] == selected_athlete]
            
            if athlete_data.empty:
                st.warning(f"No data found for {selected_athlete}")
            else:
                # Athlete Statistics
                years = sorted(athlete_data['Year'].unique())
                sports = sorted(athlete_data['Sport'].unique())
                medal_wins = athlete_data[athlete_data['Medal'].notnull()]
                
                # Display athlete info in columns
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Olympic Editions", len(years))
                with col2:
                    st.metric("Sports Competed", len(sports))
                with col3:
                    st.metric("Total Medals", medal_wins.shape[0])
                
                st.markdown(f"**Years Participated:** {', '.join(map(str, years))}")
                st.markdown(f"**Sports:** {', '.join(sports)}")
                
                st.markdown("---")
                
                # Medal Breakdown
                st.subheader("🏆 Medal Breakdown")
                if not medal_wins.empty:
                    medal_count = medal_wins['Medal'].value_counts()
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("🥇 Gold", medal_count.get('Gold', 0))
                    with col2:
                        st.metric("🥈 Silver", medal_count.get('Silver', 0))
                    with col3:
                        st.metric("🥉 Bronze", medal_count.get('Bronze', 0))
                    with col4:
                        st.metric("🏅 Total", medal_wins.shape[0])
                    
                    # Medal visualization
                    if len(medal_count) > 0:
                        medal_df = pd.DataFrame({
                            'Medal': medal_count.index,
                            'Count': medal_count.values
                        })
                        fig = px.pie(
                            medal_df,
                            values='Count',
                            names='Medal',
                            title="Medal Distribution",
                            color='Medal',
                            color_discrete_map={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32'}
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Events & Medals table
                    st.subheader("📋 Events & Medals by Year")
                    medal_table = medal_wins[['Year', 'City', 'Sport', 'Event', 'Medal']].drop_duplicates().sort_values(by='Year')
                    st.dataframe(medal_table, use_container_width=True, height=300)
                else:
                    st.info("This athlete has not won any Olympic medals.")
                
                st.markdown("---")
                
                # Height vs Weight Analysis
                st.subheader("📏 Height vs Weight Analysis by Sport")
                sport_list = sorted(df['Sport'].dropna().unique().tolist())
                sport_list.insert(0, 'Overall')
                selected_sport = st.selectbox("Select Sport", sport_list, key='athlete_sport')
                
                try:
                    sport_df = helper.weight_v_height(df, selected_sport)
                    sport_df = sport_df[pd.to_numeric(sport_df['Height'], errors='coerce').notnull()]
                    sport_df = sport_df[pd.to_numeric(sport_df['Weight'], errors='coerce').notnull()]
                    
                    if not sport_df.empty:
                        sport_df['Height'] = sport_df['Height'].astype(float)
                        sport_df['Weight'] = sport_df['Weight'].astype(float)
                        
                        fig, ax = plt.subplots(figsize=(10, 6))
                        sns.scatterplot(
                            data=sport_df, 
                            x='Weight', 
                            y='Height', 
                            hue='Medal', 
                            style='Sex', 
                            s=60, 
                            ax=ax,
                            palette={'Gold': '#FFD700', 'Silver': '#C0C0C0', 'Bronze': '#CD7F32', 'No Medal': '#808080'}
                        )
                        ax.set_title(f"Height vs Weight Distribution ({selected_sport})", fontsize=14)
                        ax.set_xlabel("Weight (kg)", fontsize=12)
                        ax.set_ylabel("Height (cm)", fontsize=12)
                        plt.legend(title='Medal / Gender', bbox_to_anchor=(1.05, 1), loc='upper left')
                        st.pyplot(fig)
                    else:
                        st.info(f"No height/weight data available for {selected_sport}.")
                except Exception as e:
                    st.warning(f"Error creating height/weight chart: {e}")
                
                st.markdown("---")
                
                # Gender Participation Trends
                st.subheader("👥 Men vs Women Participation Over the Years")
                try:
                    gender_df = helper.men_vs_women(df)
                    if not gender_df.empty:
                        fig = px.line(
                            gender_df, 
                            x="Year", 
                            y=["Male", "Female"],
                            title="Gender Participation Trends",
                            labels={'value': 'Number of Athletes', 'Year': 'Year'},
                            markers=True
                        )
                        fig.update_traces(line_width=3)
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("No gender participation data available.")
                except Exception as e:
                    st.warning(f"Error displaying gender trends: {e}")
    
    except Exception as e:
        st.error(f"An error occurred: {e}")
