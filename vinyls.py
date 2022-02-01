#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 29 19:06:26 2021

@author: kon
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt


@st.cache
def load_data():
    
    data1 = pd.read_excel('./jupyter/clean_data.xlsx')
    data2 = pd.read_csv('./jupyter/gopera-collection-20220201-1011.csv',parse_dates= ['Date Added'])
    data2['Date Added'] = pd.to_datetime(data2['Date Added'],infer_datetime_format=True, errors='coerce').dt.date

    return data1, data2


st.set_page_config(page_title='George Vinyl Collection',
                   page_icon='https://cdn-icons-png.flaticon.com/512/13/13510.png',
                   layout="wide")


st.markdown("<h1 style='text-align: center; color: #CEA49C;'>The Great Vinyl Collection</h1>", unsafe_allow_html=True)


# Load data
df_main, df_discorgs = load_data()

total_discs = len(df_main)

st.sidebar.markdown(f'<h1 style="font-size: 40px; text-align: right; color: #E9DFCA;"> {total_discs} \
                    <p style="font-size: 16px; color: #CEA49C;">discs</p>\
                    <p style="font-size: 14px; text-align: right; color: #CEA49C"><em>...and counting</em></p> </h1> \
                    ',unsafe_allow_html=True)


df_no_zero_dates = df_main.loc[df_main.Released != 0]
oldest = df_no_zero_dates.loc[df_no_zero_dates.Released.idxmin()]
newest = df_no_zero_dates.loc[df_no_zero_dates.Released.idxmax()]
average_release_date = int(df_no_zero_dates.Released.mean())

st.markdown(f"<span style='font-size:25px; color: #BEAFAF'>Newest</span> disc \
            in collection: <strong>{newest['Title']}</strong> by <strong>{newest['Artist']}</strong>,\
                <span style='font-size:20px; color: #BEAFAF'>{newest['Released']}</span>", unsafe_allow_html=True)

st.markdown(f"<span style='font-size:25px; color: #927676'>Oldest</span> \
            disc in collection: <strong>{oldest['Title']}</strong> by <strong>{oldest['Artist']}</strong>, \
                <span style='font-size:20px; color: #927676'>{oldest['Released']}</span>", unsafe_allow_html=True)

st.markdown(f"<span style='font-size:25px; color: #EFDADA'>Average</span> release date: \
            <span style='font-size:20px; color: #EFDADA'>{average_release_date}</span>", unsafe_allow_html=True)
 
if st.checkbox('Show Collection'):
    df_main

# Sidebar --------------------------------------------
# st.sidebar.image('https://scontent.fath3-3.fna.fbcdn.net/v/t1.18169-9/940994_\
#                  790953937700955_6584947839187766536_n.jpg?_nc_cat=105&ccb=1-5\
#                  &_nc_sid=973b4a&_nc_ohc=qqmyh40bN54AX91AxBh&_nc_ht=scontent.fath\
#                  3-3.fna&oh=00_AT90x3GHYOuUYAhRYIkPi9T7YGDvgTR6DfkltSlXVxkBsw&oe=61FA2A9E')
st.sidebar.markdown('<h1 style="color:#CEA49C;">Filter the data as you please.</h1>',unsafe_allow_html=True)


# Country PieChart --------------------------------------------

filtered_df = df_main[df_main['Released'] != 0]
min_date_pie = int(filtered_df['Released'].min())
max_date_pie = int(filtered_df['Released'].max())

start_date_pie, end_date_pie = st.sidebar.slider(
    'Chronological range for Pie Chart and Genre Bar Chart to consider:', 
    min_date_pie, max_date_pie, (min_date_pie,max_date_pie))
filtered_df = df_main[df_main['Released'].between(start_date_pie,end_date_pie)]


count_countries = filtered_df['Country'].value_counts().to_frame()
count_countries.reset_index(inplace=True)
count_countries.rename(columns={'index':'Country', 'Country': 'Discs'},inplace=True)

other_counts = 0
counts_values_countries = list(count_countries['Discs'])
if max(counts_values_countries) > 100:
    for value in counts_values_countries:
        if value < 5:
            other_counts += value
    
    count_countries = count_countries[count_countries['Discs'] > 30]
    count_countries.loc[-1] = ['Other', other_counts]
    count_countries.index = count_countries.index + 1
    count_countries.sort_index(inplace=True)

fig_discs_per_country = px.pie(count_countries, values='Discs', names='Country',
             color_discrete_sequence=px.colors.qualitative.Antique)
fig_discs_per_country.update_layout(title=f"Discs in collection - produced per Country between {start_date_pie}-{end_date_pie}",
                                    title_xanchor='auto',
                                    title_pad_r=5)
fig_discs_per_country.update_traces(textinfo='percent+label')

# Genre BarChart ------------------------------------

count_genres = filtered_df['Genre'].value_counts().to_frame()
count_genres.reset_index(inplace=True)
count_genres.rename(columns={'index':'Genre', 'Genre': 'Discs'},inplace=True)

show_min_genre = st.sidebar.number_input(label=f"Select minimum amount of discs to consider for each genre\
                                    ({count_genres['Discs'].min()} - {count_genres['Discs'].max()}).",   
                                    min_value = count_genres['Discs'].min(),
                                    max_value = count_genres['Discs'].max(),
                                    value = 1 + int(count_genres['Discs'].max() * 0.2))

other_counts = 0
counts_values_genres = list(count_genres['Discs'])

if max(counts_values_genres) > 100:
    for value in counts_values_genres:
        if value < 5:
            other_counts += value
    
    count_genres = count_genres[count_genres['Discs'] > show_min_genre]
    count_genres.loc[-1] = ['Other', other_counts]
    count_genres.index = count_genres.index + 1
    count_genres.sort_index(inplace=True)

fig_discs_per_genre = px.bar(count_genres, x='Genre', y='Discs', 
                             title=f"Discs in collection by Genre between {start_date_pie}-{end_date_pie}",
                             color_discrete_sequence=px.colors.qualitative.Antique,
                             color='Genre')


row1_spacer1, row1_1, row1_spacer3, row1_2, row1_spacer4 = st.columns(
    (.1, 1.6, .1, 1.6, .1)
    )

with row1_1:
    st.plotly_chart(fig_discs_per_country,use_container_width=True)
with row1_2:
    st.plotly_chart(fig_discs_per_genre,use_container_width=True)

# BarChart DateAdded --------------------------------------------

df_records_per_day = pd.DataFrame()
df_records_per_day['Records'] = df_discorgs['Date Added'].value_counts()
df_records_per_day.index.name = 'Date'
df_records_per_day.reset_index(inplace=True)

min_date_bar = df_discorgs['Date Added'].min()
max_date_bar = df_discorgs['Date Added'].max()

start_date_bar, end_date_bar = st.sidebar.slider(
    'Select range of dates for Bar Chart to consider:',
    min_date_bar, max_date_bar, (min_date_bar, max_date_bar)
)
date_range_bar = df_records_per_day[df_records_per_day['Date'].between(start_date_bar,end_date_bar)]

row2_spacer1, row2_center, ro2_spacer2 = st.columns((2,4,1))
with row2_center:
    st.write(f"Discs archieved between {start_date_bar} & {end_date_bar}")
    
c1 = alt.Chart(date_range_bar).mark_bar(size=3).encode(
    alt.X('Date', title="Date"),
    alt.Y("Records", title="Records Per Day"),
    tooltip=['Date', 'Records'],
    color=alt.Color('Date', scale=alt.Scale(scheme='darkred'))
)
st.altair_chart(c1, use_container_width=True)

#  Collection growth --------------------------


df_records_per_day.sort_values(by='Date', inplace=True)
df_records_per_day['Total'] = df_records_per_day['Records'].cumsum()



bar = alt.Chart(df_records_per_day).mark_bar(size=10).encode(
    alt.X('Date',axis=alt.Axis(
        title='Date',
        format=("%b %d"),
        )),
    alt.Y('Total:Q', title='Total'),
    tooltip=['Date', 'Total'],
    color=alt.Color('Date', scale=alt.Scale(scheme='magma'))
)

line = alt.Chart(df_records_per_day).mark_line(color='red').transform_window(
    # The field to average
    rolling_mean='mean(Total)',
    # The number of values before and after the current value to include.
    frame=[-9, 0]
).encode(
    x='Date:O',
    y='rolling_mean:Q'
)

row3_spacer1, row3_center, ro3_spacer2 = st.columns((4,5,1))
with row3_center:
    st.write("Collection Growth")
c2 = (bar+line).properties(width=600)
st.altair_chart(c2, use_container_width=True)