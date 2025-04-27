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
selected_categories = st.sidebar.multiselect("Category", categories, default=categories)
filtered = data[data['Category'].isin(selected_categories)]
# Sub-Category selector (optional)
sub_cats = sorted(filtered['Sub-Category'].unique())
selected_subcats = st.sidebar.multiselect("Sub-Category (Optional)", ['All'] + sub_cats, default=['All'])
if 'All' not in selected_subcats:
    filtered = filtered[filtered['Sub-Category'].isin(selected_subcats)]
# Year selector
years = sorted(filtered['Year'].unique())
years_options = ['All'] + years
selected_years = st.sidebar.multiselect("Year(s)", years_options, default=['All'])
if 'All' in selected_years:
    sel_years = years
else:
    sel_years = [int(y) for y in selected_years]
if not sel_years:
    st.sidebar.warning("Please select at least one year.")
    st.stop()
filtered = filtered[filtered['Year'].isin(sel_years)]

# --- Bar Chart Order Control ---
st.sidebar.header("Bar Chart Order")
order_opt = st.sidebar.radio(
    label="Order by total profit",
    options=["⬇️ Descending","⬆️ Ascending"],
    index=0,
    key="bar_order",
    label_visibility='collapsed'
)
descending = True if order_opt == "⬇️ Descending" else False

# --- Main Content ---
st.title("Sales Profit Analysis")

# --- Annual Bar Chart ---
st.subheader("Annual Profit by Category")
# Aggregate bar data
yearly = (
    filtered.groupby(['Year','Category'])['Profit']
    .sum().reset_index()
)
# Determine year order by totals
year_totals = yearly.groupby('Year')['Profit'].sum().sort_values(ascending=not descending)
sorted_years = year_totals.index.astype(str).tolist()
yearly['Year'] = yearly['Year'].astype(str)
# Plot bar chart
fig_bar = px.bar(
    yearly,
    x='Year',
    y='Profit',
    color='Category',
    barmode='group',
    labels={'Year':'Year','Profit':'Profit ($)'},
    category_orders={'Year': sorted_years},
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_bar.update_layout(
    xaxis={'categoryorder':'array','categoryarray': sorted_years},
    yaxis=dict(range=[0, yearly['Profit'].max() * 1.1])
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Line Chart Options ---
st.sidebar.header("Line Chart Options")
line_style = st.sidebar.selectbox(
    label="Line Style",
    options=['Linear','Smooth (Spline)'],
    index=0,
    key="line_style"
)
show_markers = st.sidebar.checkbox(
    label="Show Markers",
    value=True,
    key="show_markers"
)

# --- Monthly Line Chart ---
st.subheader("Monthly Profit Trend")
# Choose grouping field
group_field = 'Category' if 'All' in selected_subcats else 'Sub-Category'
line_data = (
    filtered.groupby(['Month', group_field])['Profit']
    .sum().reset_index()
)
# Order months
line_data['Month'] = pd.Categorical(line_data['Month'], categories=month_order, ordered=True)
line_data = line_data.sort_values('Month')
# Plot line chart
fig_line = px.line(
    line_data,
    x='Month',
    y='Profit',
    color=group_field,
    labels={'Month':'Month','Profit':'Profit ($)'},
    category_orders={'Month': month_order},
    color_discrete_sequence=px.colors.qualitative.Bold
)
fig_line.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style=='Smooth (Spline)' else 'linear'
)
fig_line.update_layout(
    yaxis=dict(range=[0, line_data['Profit'].max() * 1.1])
)
st.plotly_chart(fig_line, use_container_width=True)

# --- Table View & Download ---
st.subheader("Profit Table by Selection")
table_df = (
    filtered.groupby(['Year','Month'])['Profit']
    .sum().reset_index()
)
# Sort table by year then month
table_df['Month'] = pd.Categorical(table_df['Month'], categories=month_order, ordered=True)
table_df = table_df.sort_values(['Year','Month'])
st.dataframe(table_df)
# Download CSV
tbl_csv = table_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Table as CSV",
    data=tbl_csv,
    file_name='profit_table.csv',
    mime='text/csv'
)
