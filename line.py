import streamlit as st
import pandas as pd
import plotly.express as px

# --- Streamlit App Config ---
st.set_page_config(page_title="Sales Profit Analysis", layout="wide")

# --- Load and Prepare Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('Sales Dataset.csv')
    df['Date'] = pd.to_datetime(df['Year-Month'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%b')
    return df

data = load_data()

# --- Title ---
st.title("Sales Profit Analysis")

# --- Filters: Category & Sub-Category ---
categories = data['Category'].unique()
selected_categories = st.multiselect("Select Category(s)", categories, default=categories)
filtered = data[data['Category'].isin(selected_categories)]

sub_cats = filtered['Sub-Category'].unique()
selected_sub = st.multiselect("Select Sub-Category(s) (Optional)", sub_cats)
if selected_sub:
    filtered = filtered[filtered['Sub-Category'].isin(selected_sub)]

# --- Filter by Year (mandatory) ---
available_years = sorted(filtered['Year'].unique())
selected_year = st.selectbox("Select Year", available_years)
filtered = filtered[filtered['Year'] == selected_year]

# --- Define Month Order ---
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# --- Line Chart Data Preparation ---
line_data = (
    filtered.groupby(['Month','Category'])['Profit']
    .sum()
    .reset_index()
)
line_data['Month'] = pd.Categorical(line_data['Month'], categories=month_order, ordered=True)
line_data = line_data.sort_values('Month')

# --- Line Chart Controls ---
line_style = st.selectbox("Select Line Style", ["Linear", "Smooth (Spline)"])
show_markers = st.checkbox("Show Markers (Dots)", value=True)

# --- Line Chart ---
line_fig = px.line(
    line_data,
    x="Month",
    y="Profit",
    color="Category",
    labels={"Profit": "Profit ($)", "Month": "Month"},
    title="Monthly Profit by Category",
    color_discrete_sequence=px.colors.qualitative.Bold
)
line_fig.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style == "Smooth (Spline)" else 'linear'
)
line_fig.update_layout(
    xaxis={'categoryorder': 'array', 'categoryarray': month_order},
    yaxis={'range': [0, line_data['Profit'].max() * 1.1]},
    xaxis_title="Month",
    yaxis_title="Profit"
)
st.plotly_chart(line_fig, use_container_width=True)

# --- Profit Table by Month ---
st.subheader("📋 Profit Table by Month")
table = (
    filtered.groupby(['Month','Category'])['Profit']
    .sum()
    .reset_index()
)
table['Month'] = pd.Categorical(table['Month'], categories=month_order, ordered=True)
table = table.sort_values(['Month','Category'])
st.dataframe(table)

# --- Bar Chart ---
st.subheader("📊 Monthly Profit Comparison by Category (Bar Chart)")
bar_fig = px.bar(
    table,
    x="Month",
    y="Profit",
    color="Category",
    barmode="group",
    labels={"Profit": "Profit ($)", "Month": "Month"},
    title="Monthly Profit by Category",
    color_discrete_sequence=px.colors.qualitative.Bold
)
bar_fig.update_layout(
    xaxis={'categoryorder': 'array', 'categoryarray': month_order},
    yaxis={'range': [0, table['Profit'].max() * 1.1]},
    xaxis_title="Month",
    yaxis_title="Profit"
)
st.plotly_chart(bar_fig, use_container_width=True)

# --- Download Table as CSV ---
st.subheader("Download Profit Data as CSV")
csv = table.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download CSV",
    data=csv,
    file_name='profit_data.csv',
    mime='text/csv'
)
