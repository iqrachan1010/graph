#Line grapgh 

import streamlit as st
import pandas as pd

# Load dataset
data = pd.read_csv('Sales Dataset.csv')

# Prepare unique filter options
categories = data['Category'].unique()

# Streamlit UI
st.title("Sales Profit Analysis")

# Filters
selected_category = st.selectbox("Select Category", categories)

# Filter data by selected category
filtered_data = data[data['Category'] == selected_category]

# Optional Sub-category filter
sub_categories = filtered_data['Sub-Category'].unique()
sub_category = st.selectbox("Select Sub-Category (Optional)", ['All'] + list(sub_categories))

if sub_category != 'All':
    filtered_data = filtered_data[filtered_data['Sub-Category'] == sub_category]

# Year selection
filtered_data['Year'] = pd.to_datetime(filtered_data['Year-Month']).dt.year
selected_year = st.selectbox("Select Year", ['All'] + sorted(filtered_data['Year'].unique().tolist()))

if selected_year != 'All':
    filtered_data = filtered_data[filtered_data['Year'] == selected_year]

# Group by Year-Month
filtered_data_grouped = filtered_data.groupby('Year-Month')['Profit'].sum().reset_index()
filtered_data_grouped = filtered_data_grouped.sort_values('Year-Month')

# Display chart and data
st.line_chart(filtered_data_grouped.set_index('Year-Month')['Profit'])
st.dataframe(filtered_data_grouped)
