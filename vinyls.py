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
    
    data = pd.read_excel('./jupyter/gopera_collection.xlsx',parse_dates= ['Date Added'])
    data['Date Added'] = pd.to_datetime(data['Date Added'],infer_datetime_format=True, errors='coerce').dt.date

    return data


st.set_page_config(page_title='George Vinyl Collection',
                   page_icon='https://cdn-icons-png.flaticon.com/512/13/13510.png',
                   layout="wide")


st.markdown("<h1 style='text-align: center; color: #CEA49C;'>The Great Vinyl Collection</h1>", unsafe_allow_html=True)


# Load data
df = load_data()

total_discs = len(df)

st.sidebar.markdown(f'<h1 style="font-size: 40px; text-align: right; color: #E9DFCA;"> {total_discs} \
                    <p style="font-size: 16px; color: #CEA49C;">discs</p>\
                    <p style="font-size: 14px; text-align: right; color: #CEA49C"><em>...and counting</em></p> </h1> \
                    ',unsafe_allow_html=True)

if st.checkbox('Show Collection'):
    df

# Sidebar --------------------------------------------
# st.sidebar.image('https://scontent.fath3-3.fna.fbcdn.net/v/t1.18169-9/940994_\
#                  790953937700955_6584947839187766536_n.jpg?_nc_cat=105&ccb=1-5\
#                  &_nc_sid=973b4a&_nc_ohc=qqmyh40bN54AX91AxBh&_nc_ht=scontent.fath\
#                  3-3.fna&oh=00_AT90x3GHYOuUYAhRYIkPi9T7YGDvgTR6DfkltSlXVxkBsw&oe=61FA2A9E')
st.sidebar.markdown('<h1 style="color:#CEA49C;">Filter the data as you please.</h1>',unsafe_allow_html=True)


# Pie chart --------------------------------------------
df = df[df['Released'] != 0]
min_date_pie = int(df['Released'].min())
max_date_pie = int(df['Released'].max())

start_date_pie, end_date_pie = st.sidebar.slider(
    'Chronological range for Pie Chart to consider:', 
    min_date_pie, max_date_pie, (min_date_pie,max_date_pie))
filtered_df = df[df['Released'].between(start_date_pie,end_date_pie)]


counts_df = filtered_df['Country'].value_counts().to_frame()
counts_df.reset_index(inplace=True)
counts_df.rename(columns={'index':'Country', 'Country': 'Discs'},inplace=True)

other_counts = 0
counts_values = list(counts_df['Discs'])
if max(counts_values) > 100:
    for value in counts_values:
        if value < 5:
            other_counts += value
    
    counts_df = counts_df[counts_df['Discs'] > 30]
    counts_df.loc[-1] = ['Other', other_counts]
    counts_df.index = counts_df.index + 1
    counts_df.sort_index(inplace=True)

fig_discs_per_country = px.pie(counts_df, values='Discs', names='Country',
             title=f"Discs in collection - produced per Country between {start_date_pie}-{end_date_pie}",
             color_discrete_sequence=px.colors.qualitative.Antique)
fig_discs_per_country.update_traces(textinfo='percent+label')

row1_space1, row1_center, row1_space2 = st.columns((1,4,1))

with row1_center:
    st.plotly_chart(fig_discs_per_country)


# BarChart for DateAdded --------------------------------------------
df_records_per_day = pd.DataFrame()
df_records_per_day['Records'] = df['Date Added'].value_counts()
df_records_per_day.index.name = 'Date'
df_records_per_day.reset_index(inplace=True)

min_date_bar = df['Date Added'].min()
max_date_bar = df['Date Added'].max()

start_date_bar, end_date_bar = st.sidebar.slider(
    'Select range of dates for Bar Chart to consider:',
    min_date_bar, max_date_bar, (min_date_bar, max_date_bar)
)
date_range_bar = df_records_per_day[df_records_per_day['Date'].between(start_date_bar,end_date_bar)]

row2_space1, row2_center, ro2_space2 = st.columns((2,4,1))
with row2_center:
    st.write(f"Discs archieved between {start_date_bar} & {end_date_bar}")
    
c1 = alt.Chart(date_range_bar).mark_bar().encode(
    alt.X('Date', title="Date"),
    alt.Y("Records", title="Records Per Day"),
    tooltip=['Date', 'Records'],
    color=alt.Color('Date', scale=alt.Scale(scheme='darkred'))
)
st.altair_chart(c1, use_container_width=True)

#  Collection growth --------------------------


df_records_per_day.sort_values(by='Date', inplace=True)
df_records_per_day['Total'] = df_records_per_day['Records'].cumsum()



bar = alt.Chart(df_records_per_day).mark_bar(size=12).encode(
    alt.X('Date',axis=alt.Axis(
        title='Date',
        format=("%b %d"),
        # tickCount = {"interval": "month", "step": 3}
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

row3_space1, row3_center, ro3_space2 = st.columns((4,5,1))
with row3_center:
    st.write("Collection Growth")
c2 = (bar+line).properties(width=600)
st.altair_chart(c2, use_container_width=True)


