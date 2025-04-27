import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
data = pd.read_csv('Sales Dataset.csv')

# Streamlit UI
st.title("Sales Profit Analysis")

# --- Filters ---
categories = data['Category'].unique()
selected_categories = st.multiselect("Select Category(s)", categories, default=categories)

filtered_data = data[data['Category'].isin(selected_categories)]

sub_categories = filtered_data['Sub-Category'].unique()
sub_category = st.selectbox("Select Sub-Category (Optional)", ['All'] + list(sub_categories))
if sub_category != 'All':
    filtered_data = filtered_data[filtered_data['Sub-Category'] == sub_category]

# --- Date Processing ---
filtered_data['Date'] = pd.to_datetime(filtered_data['Year-Month'])
filtered_data['Year'] = filtered_data['Date'].dt.year
filtered_data['Month'] = filtered_data['Date'].dt.strftime('%b')
filtered_data['YearMonthLabel'] = filtered_data['Date'].dt.strftime('%Y-%b')

# --- Year Selection ---
available_years = sorted(filtered_data['Year'].unique())
selected_years = st.multiselect("Select Year(s)", available_years)
if not selected_years:
    st.warning("⚠️ Please select at least one year to continue.")
    st.stop()
filtered_data = filtered_data[filtered_data['Year'].isin(selected_years)]

# --- Moving Average Option ---
smoothing_option = st.selectbox("Apply Moving Average Smoothing?", ["None", "3-month", "6-month"])

# --- Line Chart Preparation ---
filtered_data_grouped = (
    filtered_data
    .groupby(['Date', 'YearMonthLabel', 'Category'])['Profit']
    .sum()
    .reset_index()
    .sort_values('Date')
)

if smoothing_option != "None":
    window_size = int(smoothing_option.split('-')[0])
    filtered_data_grouped['Profit'] = (
        filtered_data_grouped
        .groupby('Category')['Profit']
        .transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())
    )

# --- Line Chart Display ---
line_style = st.selectbox("Select Line Style", ["Linear", "Smooth (Spline)"])
show_markers = st.checkbox("Show Markers (Dots)", value=True)

line_fig = px.line(
    filtered_data_grouped,
    x="YearMonthLabel",
    y="Profit",
    color="Category",
    labels={"Profit": "Profit ($)", "YearMonthLabel": "Month-Year"},
    title="Monthly Profit by Category",
    hover_data={"YearMonthLabel": True, "Profit": ":,.2f", "Category": True},
    color_discrete_sequence=px.colors.qualitative.Bold
)

line_fig.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style == "Smooth (Spline)" else 'linear'
)

line_fig.update_layout(
    xaxis={'categoryorder': 'array', 'categoryarray': filtered_data_grouped['YearMonthLabel'].unique()},
    yaxis=dict(range=[0, filtered_data_grouped['Profit'].max() * 1.1]),
    xaxis_title="Month-Year",
    yaxis_title="Profit"
)

st.plotly_chart(line_fig, use_container_width=True)

# --- Table View ---
st.subheader("📋 Profit Table by Year and Month")
table_data = (
    filtered_data
    .groupby(['Year', 'Month'])['Profit']
    .sum()
    .reset_index()
    .sort_values(['Year', 'Month'])
)

st.dataframe(table_data)

# --- Bar Chart ---
st.subheader("📊 Monthly Profit by Category (Bar Chart)")

bar_data = (
    filtered_data
    .groupby(['YearMonthLabel', 'Category'])['Profit']
    .sum()
    .reset_index()
    .sort_values('YearMonthLabel')
)

bar_fig = px.bar(
    bar_data,
    x="YearMonthLabel",
    y="Profit",
    color="Category",
    barmode="group",
    labels={"Profit": "Profit ($)", "YearMonthLabel": "Month-Year"},
    title="Monthly Profit Comparison by Category",
    color_discrete_sequence=px.colors.qualitative.Bold
)

st.plotly_chart(bar_fig, use_container_width=True)

# --- Download Table as CSV ---
csv = table_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Profit Table as CSV",
    data=csv,
    file_name='profit_table.csv',
    mime='text/csv'
)
