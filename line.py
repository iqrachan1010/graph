#line

import streamlit as st
import pandas as pd

# Load dataset
data = pd.read_csv('Sales Dataset.csv')

# Prepare unique filter options
categories = data['Category'].unique()

# Streamlit UI
st.title("Sales Profit Analysis")

# Filters
selected_categories = st.multiselect("Select Category(s)", categories, default=categories)

# Filter data by selected categories
filtered_data = data[data['Category'].isin(selected_categories)]

# Optional Sub-category filter
sub_categories = filtered_data['Sub-Category'].unique()
sub_category = st.selectbox("Select Sub-Category (Optional)", ['All'] + list(sub_categories))

if sub_category != 'All':
    filtered_data = filtered_data[filtered_data['Sub-Category'] == sub_category]

# Extract Year and Month
filtered_data['Year'] = pd.to_datetime(filtered_data['Year-Month']).dt.year
filtered_data['Month'] = pd.to_datetime(filtered_data['Year-Month']).dt.strftime('%b')

# Group by Month and Category
filtered_data_grouped = filtered_data.groupby(['Year', 'Month', 'Category'])['Profit'].sum().reset_index()

# Year selection below the x-axis
selected_year = st.selectbox("Select Year", ['All'] + sorted(filtered_data_grouped['Year'].unique().tolist()))

if selected_year != 'All':
    filtered_data_grouped = filtered_data_grouped[filtered_data_grouped['Year'] == selected_year]

# Pivot data for plotting
pivot_data = filtered_data_grouped.pivot_table(index='Month', columns='Category', values='Profit', fill_value=0)

# Display chart with labels
st.line_chart(pivot_data, use_container_width=True, y_axis_title="Profit")
st.dataframe(pivot_data.reset_index())
