import streamlit as st
import pandas as pd
import plotly.express as px

# --- App Config ---
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
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# --- Title ---
st.title("Sales Profit Analysis")

# --- Filters ---
categories = sorted(data['Category'].unique())
selected_categories = st.multiselect("Select Category(s)", categories, default=categories)
filtered = data[data['Category'].isin(selected_categories)]

sub_cats = sorted(filtered['Sub-Category'].unique())
selected_subcats = st.multiselect("Select Sub-Category(s) (Optional)", ['All'] + sub_cats, default=['All'])
if 'All' not in selected_subcats:
    filtered = filtered[filtered['Sub-Category'].isin(selected_subcats)]

years = sorted(filtered['Year'].unique())
selected_years = st.multiselect("Select Year(s)", ['All'] + years, default=['All'])
if 'All' in selected_years:
    selected_years = years
elif not selected_years:
    st.warning("⚠️ Please select at least one year.")
    st.stop()
filtered = filtered[filtered['Year'].isin(selected_years)]

# --- Bar Chart Order Option ---
order_option = st.selectbox(
    "Order bars by total profit:",
    ["Descending", "Ascending"],
    index=0
)

# --- Bar Chart ---
st.subheader("Annual Profit by Category")
grouped_bar = (
    filtered
    .groupby(['Year', 'Category'])['Profit']
    .sum()
    .reset_index()
)
# Convert Year to string for x-axis
grouped_bar['Year_str'] = grouped_bar['Year'].astype(str)
# Compute total profit per year
year_totals = grouped_bar.groupby('Year_str')['Profit'].sum()
# Sort years according to order_option
sorted_years = (
    year_totals.sort_values(ascending=(order_option == "Ascending")).index.tolist()
)

fig_bar = px.bar(
    grouped_bar,
    x='Year_str', y='Profit', color='Category', barmode='group',
    labels={'Year_str':'Year', 'Profit':'Profit ($)'},
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_bar.update_layout(
    xaxis_title='Year',
    yaxis_title='Profit',
    yaxis=dict(range=[0, grouped_bar['Profit'].max() * 1.1]),
    xaxis=dict(categoryorder='array', categoryarray=sorted_years)
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Line Chart ---
st.subheader("Monthly Profit Trend")
if 'All' in selected_subcats:
    group_field = 'Category'
else:
    group_field = 'Sub-Category'

grouped_line = (
    filtered
    .groupby(['Month', group_field])['Profit']
    .sum()
    .reset_index()
)
# Order months
grouped_line['Month'] = pd.Categorical(grouped_line['Month'], categories=month_order, ordered=True)
grouped_line = grouped_line.sort_values('Month')

# Layout: selectors beside chart
col1, col2 = st.columns([4, 1])
with col2:
    line_style = st.selectbox("Line Style", ['Linear', 'Smooth (Spline)'])
    show_markers = st.checkbox("Show Markers", True)
with col1:
    fig_line = px.line(
        grouped_line,
        x='Month', y='Profit', color=group_field,
        labels={'Month':'Month','Profit':'Profit ($)'},
        color_discrete_sequence=px.colors.qualitative.Bold
    )
    fig_line.update_traces(
        mode='lines+markers' if show_markers else 'lines',
        line_shape='spline' if line_style == 'Smooth (Spline)' else 'linear'
    )
    fig_line.update_layout(
        xaxis_title='Month',
        yaxis_title='Profit',
        yaxis=dict(range=[0, grouped_line['Profit'].max() * 1.1]),
        xaxis=dict(categoryorder='array', categoryarray=month_order)
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- Table View ---
st.subheader("Profit Table by Selection")
table = (
    filtered
    .groupby(['Year', 'Month'])['Profit']
    .sum()
    .reset_index()
)
# Order table by Year then Month
table['Month'] = pd.Categorical(table['Month'], categories=month_order, ordered=True)
table = table.sort_values(['Year', 'Month'])
st.dataframe(table)

# --- Download CSV ---
csv = table.to_csv(index=False).encode('utf-8')
st.download_button("Download Table as CSV", csv, "profit_table.csv", "text/csv")
