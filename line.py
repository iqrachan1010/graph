import streamlit as st
import pandas as pd
import plotly.express as px

# --- Streamlit App: Sales Profit Analysis ---
st.set_page_config(layout="wide")
st.title("Sales Profit Analysis")

# --- Load and Filter Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('Sales Dataset.csv')
    df['Date'] = pd.to_datetime(df['Year-Month'])
    df['Year'] = df['Date'].dt.year
    df['YearMonthLabel'] = df['Date'].dt.strftime('%Y-%b')
    return df

data = load_data()

# Category filter
categories = data['Category'].unique()
selected_categories = st.multiselect(
    "Select Category(s)", categories, default=None, help="Choose one or more categories"
)
if not selected_categories:
    st.error("⚠️ Please select at least one category.")
    st.stop()
filtered = data[data['Category'].isin(selected_categories)]

# Sub-category filter
sub_categories = filtered['Sub-Category'].unique()
selected_sub = st.selectbox(
    "Select Sub-Category (Optional)", ['All'] + list(sub_categories)
)
if selected_sub != 'All':
    filtered = filtered[filtered['Sub-Category'] == selected_sub]

# Year filter (no 'All' option)
years = sorted(filtered['Year'].unique())
selected_years = st.multiselect(
    "Select Year(s)", years, default=None, help="Must select at least one year"
)
if not selected_years:
    st.error("⚠️ Please select at least one year.")
    st.stop()
filtered = filtered[filtered['Year'].isin(selected_years)]

# --- Prepare for Plotting ---
# Aggregate profits by Date and Category
time_series = (
    filtered
    .groupby(['Date', 'YearMonthLabel', 'Category'])['Profit']
    .sum()
    .reset_index()
    .sort_values('Date')
)

# Smoothing option
smoothing = st.selectbox("Moving Average Smoothing", ["None", "3-month", "6-month"])
if smoothing != "None":
    window = int(smoothing.split('-')[0])
    time_series['Profit'] = (
        time_series.groupby('Category')['Profit']
        .transform(lambda x: x.rolling(window, min_periods=1).mean())
    )

# Line style and markers
line_mode = st.selectbox("Line Style", ["Linear", "Smooth (Spline)"])
show_markers = st.checkbox("Show Markers", value=True)

# --- Plot Line Chart ---
fig = px.line(
    time_series,
    x='YearMonthLabel',
    y='Profit',
    color='Category',
    labels={'Profit': 'Profit ($)', 'YearMonthLabel': 'Month-Year'},
    hover_data={'YearMonthLabel': True, 'Profit': ':,.2f'},
    color_discrete_sequence=px.colors.qualitative.Bold,
    title="Monthly Profit Trend by Category"
)
fig.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_mode == "Smooth (Spline)" else 'linear'
)
fig.update_layout(
    xaxis=dict(
        categoryorder='array',
        categoryarray=time_series['YearMonthLabel'].unique()
    ),
    yaxis=dict(title='Profit ($)', range=[0, time_series['Profit'].max() * 1.1]),
    xaxis_title='Month-Year'
)
st.plotly_chart(fig, use_container_width=True)

# --- Show Table ---
st.subheader("Profit Table by Year and Month")
table = (
    filtered
    .groupby([filtered['Date'].dt.year.rename('Year'), filtered['Date'].dt.strftime('%b').rename('Month')])['Profit']
    .sum()
    .reset_index()
    .sort_values(['Year', 'Month'])
)
st.dataframe(table)

# --- CSV Download ---
csv = table.to_csv(index=False).encode('utf-8')
st.download_button("Download Table as CSV", csv, "profit_table.csv", "text/csv")
