import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.colors import n_colors

# --- App Config ---
st.set_page_config(page_title="Sales Profit Analysis", layout="wide")

# --- Load Data ---
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

# --- Filters ---
categories = data['Category'].unique()
selected_categories = st.multiselect("Select Category(s)", categories, default=categories)
filtered = data[data['Category'].isin(selected_categories)]

subcats = filtered['Sub-Category'].unique()
selected_subcats = st.multiselect("Select Sub-Category(s)", subcats, default=subcats)
filtered = filtered[filtered['Sub-Category'].isin(selected_subcats)]

# --- Prepare Monthly Data for Line Chart ---
filtered_line = (
    filtered
    .groupby(['Date','Month','Category','Sub-Category'])['Profit']
    .sum()
    .reset_index()
    .sort_values('Date')
)

# --- Layout: Chart and Controls Side by Side ---
available_years = sorted(filtered_line['Date'].dt.year.unique())
col_chart, col_controls = st.columns([4,1], gap="small")

with col_controls:
    selected_year = st.selectbox("Select Year", available_years)
    line_style = st.selectbox("Line Style", ["Linear", "Smooth (Spline)"])
    show_markers = st.checkbox("Show Markers", value=True)

# Filter to selected year
df_year = filtered_line[filtered_line['Date'].dt.year == selected_year]

# --- Generate Sub-Category Color Shades ---
cats = df_year['Category'].unique()
base_colors = px.colors.qualitative.Bold
cat_color_map = {cat: base_colors[i % len(base_colors)] for i, cat in enumerate(cats)}
sub_color_map = {}
for cat in cats:
    sub_list = df_year[df_year['Category'] == cat]['Sub-Category'].unique()
    shades = n_colors('rgb(255,255,255)', cat_color_map[cat], len(sub_list), colortype='rgb')
    for sub, shade in zip(sub_list, shades):
        sub_color_map[sub] = shade

# --- Plot Line Chart ---
fig = px.line(
    df_year,
    x='Month',
    y='Profit',
    color='Sub-Category',
    labels={'Profit':'Profit ($)', 'Month':'Month'},
    title=f"Monthly Profit by Sub-Category ({selected_year})",
    color_discrete_map=sub_color_map,
    hover_data={'Month':True, 'Profit':':,.2f', 'Sub-Category':True}
)
fig.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style == "Smooth (Spline)" else 'linear'
)
# Order x-axis months Jan to Dec
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
fig.update_layout(
    xaxis={'categoryorder':'array', 'categoryarray':month_order},
    yaxis={'range':[0, df_year['Profit'].max() * 1.1]},
    xaxis_title='Month',
    yaxis_title='Profit'
)

with col_chart:
    st.plotly_chart(fig, use_container_width=True)

# --- Bar Chart ---
st.subheader("Monthly Profit Comparison by Category (Bar)")
bar_data = (
    filtered
    .groupby(['Year','Month','Category'])['Profit']
    .sum()
    .reset_index()
)

# Order month
bar_data['Month'] = pd.Categorical(bar_data['Month'], categories=month_order, ordered=True)
bar_data = bar_data.sort_values(['Year','Month'])

bar_fig = px.bar(
    bar_data,
    x='Month',
    y='Profit',
    color='Category',
    barmode='group',
    labels={'Profit':'Profit ($)', 'Month':'Month'},
    title=f"Monthly Profit by Category ({selected_year})",
    color_discrete_sequence=px.colors.qualitative.Bold
)
bar_fig.update_layout(
    yaxis={'range':[0, bar_data['Profit'].max() * 1.1]},
    xaxis_title='Month',
    yaxis_title='Profit'
)
st.plotly_chart(bar_fig, use_container_width=True)

# --- Profit Table & Download ---
st.subheader("Profit Table by Year and Month")
table = (
    df_year
    .groupby(['Year', 'Month'])['Profit']
    .sum()
    .reset_index()
    .sort_values(['Year','Month'])
)
st.dataframe(table)
csv = table.to_csv(index=False).encode('utf-8')
st.download_button("Download Table as CSV", csv, "profit_table.csv", "text/csv")
