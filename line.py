import streamlit as st
import pandas as pd
import plotly.express as px

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

# Create Date, Year, Month, and YearMonthLabel columns
filtered_data['Date'] = pd.to_datetime(filtered_data['Year-Month'])
filtered_data['Year'] = filtered_data['Date'].dt.year
filtered_data['Month'] = filtered_data['Date'].dt.strftime('%b')
filtered_data['YearMonthLabel'] = filtered_data['Date'].dt.strftime('%Y-%b')

# Year selection
available_years = sorted(filtered_data['Year'].unique())
selected_years = st.multiselect("Select Year(s)", available_years, default=available_years)

# Filter data based on selected years
filtered_data = filtered_data[filtered_data['Year'].isin(selected_years)]

# Group for plotting
filtered_data_grouped = filtered_data.groupby(['Date', 'YearMonthLabel', 'Category'])['Profit'].sum().reset_index()
filtered_data_grouped = filtered_data_grouped.sort_values('Date')

# Moving Average Smoothing option
smoothing_option = st.selectbox("Apply Moving Average Smoothing?", ["None", "3-month", "6-month"])

if smoothing_option != "None":
    window_size = int(smoothing_option.split('-')[0])
    filtered_data_grouped['Profit'] = (
        filtered_data_grouped
        .groupby('Category')['Profit']
        .transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())
    )

# Dropdown for line style
line_style = st.selectbox("Select Line Style", ["Linear", "Smooth (Spline)"])

# Checkbox for markers
show_markers = st.checkbox("Show Markers (Dots)", value=True)

# Create the line chart
fig = px.line(
    filtered_data_grouped,
    x="YearMonthLabel",
    y="Profit",
    color="Category",
    labels={"Profit": "Profit ($)", "YearMonthLabel": "Month-Year"},
    title="Monthly Profit by Category",
    hover_data={
        "YearMonthLabel": True,
        "Profit": ":,.2f",
        "Category": True
    },
    color_discrete_sequence=px.colors.qualitative.Bold
)

fig.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style == "Smooth (Spline)" else 'linear'
)

# Proper chronological x-axis order
fig.update_layout(
    xaxis={
        'categoryorder': 'array',
        'categoryarray': filtered_data_grouped.sort_values('Date')['YearMonthLabel'].unique()
    },
    yaxis=dict(range=[0, filtered_data_grouped['Profit'].max() * 1.1]),
    xaxis_title="Month-Year",
    yaxis_title="Profit"
)

# Show the chart
st.plotly_chart(fig, use_container_width=True)

# 📋 Create and show table view
st.subheader("📋 Profit Table by Year and Month")
table_data = (
    filtered_data
    .groupby(['Year', 'Month'])['Profit']
    .sum()
    .reset_index()
    .sort_values(['Year', 'Month'])
)
st.dataframe(table_data)

# 📥 Download Table as CSV
csv = table_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Profit Table as CSV",
    data=csv,
    file_name='profit_table.csv',
    mime='text/csv'
)
