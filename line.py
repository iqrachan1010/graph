import streamlit as st
import pandas as pd
import plotly.express as px

# --- App Configuration ---
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

# --- Sidebar Filters ---
st.sidebar.header("Filters")
# Category selector
categories = sorted(data['Category'].unique())
selected_categories = st.sidebar.multiselect(
    "Category", categories, default=categories, key="cat_filter"
)
filtered = data[data['Category'].isin(selected_categories)]

# Sub-Category selector (optional)
sub_cats = sorted(filtered['Sub-Category'].unique())
selected_subcats = st.sidebar.multiselect(
    "Sub-Category (Optional)", ['All'] + sub_cats, default=['All'], key="sub_filter"
)
if 'All' not in selected_subcats:
    filtered = filtered[filtered['Sub-Category'].isin(selected_subcats)]

# Year selector (including All)
years = sorted(filtered['Year'].unique())
year_options = ['All'] + [str(y) for y in years]
selected_years = st.sidebar.multiselect(
    "Year(s)", year_options, default=['All'], key="year_filter"
)
if 'All' in selected_years:
    sel_years = years
else:
    sel_years = [int(y) for y in selected_years]
if not sel_years:
    st.sidebar.warning("Please select at least one year.")
    st.stop()
filtered = filtered[filtered['Year'].isin(sel_years)]

# --- Line Chart Options ---
st.sidebar.header("Line Chart Options")
line_style = st.sidebar.selectbox(
    "Line Style", ['Linear','Smooth (Spline)'], index=0, key="line_style"
)
show_markers = st.sidebar.checkbox(
    "Show Markers", True, key="markers"
)

# --- Main Content ---
st.title("Sales Profit Analysis")

# --- Annual Bar Chart ---
st.subheader("Annual Profit by Category")
# Aggregate bar data
yearly = filtered.groupby(['Year','Category'])['Profit'].sum().reset_index()
# Convert Year to string for categorical axis
yearly['Year'] = yearly['Year'].astype(str)
# Determine sorted order of years
year_list = sorted(filtered['Year'].unique())
year_list_str = [str(y) for y in year_list]
# Plot bar chart with categorical x-axis
fig_bar = px.bar(
    yearly,
    x='Year', y='Profit', color='Category', barmode='group',
    labels={'Year':'Year','Profit':'Profit ($)'},
    category_orders={'Year': year_list_str},
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_bar.update_layout(
    xaxis={'type':'category', 'categoryorder':'array', 'categoryarray': year_list_str},
    yaxis={'range': [0, yearly['Profit'].max() * 1.1]}
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Monthly Line Chart ---
st.subheader("Monthly Profit Trend")
# Determine grouping field
group_field = 'Category' if 'All' in selected_subcats else 'Sub-Category'
line_df = (
    filtered.groupby(['Month', group_field])['Profit']
    .sum().reset_index()
)
line_df['Month'] = pd.Categorical(line_df['Month'], categories=month_order, ordered=True)
line_df = line_df.sort_values('Month')
fig_line = px.line(
    line_df,
    x='Month', y='Profit', color=group_field,
    labels={'Month':'Month','Profit':'Profit ($)'},
    category_orders={'Month': month_order},
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_line.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style=='Smooth (Spline)' else 'linear'
)
fig_line.update_layout(
    yaxis={'range':[0, line_df['Profit'].max()*1.1]}
)
st.plotly_chart(fig_line, use_container_width=True)

# --- Table View & Download ---
st.subheader("Profit Table by Selection")
table_df = (
    filtered.groupby(['Year','Month','Category','Sub-Category'])['Profit']
    .sum()
    .reset_index()
)
# Order Month Column
table_df['Month'] = pd.Categorical(table_df['Month'], categories=month_order, ordered=True)
table_df = table_df.sort_values(['Year','Month','Category','Sub-Category'])
st.dataframe(table_df)
tbl_csv = table_df.to_csv(index=False).encode('utf-8')
st.download_button("Download Table as CSV", tbl_csv, "profit_table.csv", "text/csv")
