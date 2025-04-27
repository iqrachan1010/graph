import streamlit as st  
import pandas as pd  
import plotly.express as px  
from plotly.colors import n_colors  

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

# --- Title ---  
st.title("Sales Profit Analysis")  

# --- Layout: Filters and Controls ---  
col_filter, col_controls = st.columns([3, 1], gap="small")  

with col_filter:  
    # Category Selection  
    categories = data['Category'].unique()  
    selected_categories = st.multiselect("Select Category(s)", categories, default=categories)  
    df_filtered = data[data['Category'].isin(selected_categories)]  
    
    # Sub-Category Selection  
    subcats = df_filtered['Sub-Category'].unique()  
    selected_subcats = st.multiselect("Select Sub-Category(s)", subcats, default=subcats)  
    df_filtered = df_filtered[df_filtered['Sub-Category'].isin(selected_subcats)]  

with col_controls:  
    # Year Selection (mandatory)  
    available_years = sorted(df_filtered['Year'].unique())  
    selected_year = st.selectbox("Select Year", available_years)  
    
    # Line Chart Style Controls  
    line_style = st.selectbox("Line Style", ["Linear", "Smooth (Spline)"])  
    show_markers = st.checkbox("Show Markers", value=True)  

# Filter by selected year  
df_year = df_filtered[df_filtered['Year'] == selected_year]  

# Month ordering for x-axis  
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']  

# --- Prepare Line Chart Data ---  
df_line = (
    df_year
    .groupby(['Month','Category','Sub-Category'])['Profit']
    .sum()
    .reset_index()
)
# Order months  
df_line['Month'] = pd.Categorical(df_line['Month'], categories=month_order, ordered=True)  
df_line = df_line.sort_values('Month')  

# --- Generate Color Map for Sub-Categories ---  
base_colors = px.colors.qualitative.Bold  
cat_list = df_line['Category'].unique()  
cat_color_map = {cat: base_colors[i % len(base_colors)] for i, cat in enumerate(cat_list)}  
sub_color_map = {}  
for cat in cat_list:  
    subs = df_line[df_line['Category'] == cat]['Sub-Category'].unique()  
    shades = n_colors('rgb(255,255,255)', cat_color_map[cat], len(subs), colortype='rgb')  
    for sub, shade in zip(subs, shades):  
        sub_color_map[sub] = shade  

# --- Plot Line Chart ---  
fig_line = px.line(
    df_line,
    x='Month',
    y='Profit',
    color='Sub-Category',
    labels={'Profit':'Profit ($)','Month':'Month'},
    title=f"Monthly Profit by Sub-Category ({selected_year})",
    color_discrete_map=sub_color_map,
    hover_data={'Month':True,'Profit':':,.2f','Sub-Category':True}
)
fig_line.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style == "Smooth (Spline)" else 'linear'
)
fig_line.update_layout(
    xaxis={'categoryorder':'array','categoryarray':month_order},
    yaxis={'range':[0, df_line['Profit'].max() * 1.1]},
    xaxis_title='Month',
    yaxis_title='Profit'
)

st.plotly_chart(fig_line, use_container_width=True)  

# --- Plot Bar Chart ---  
st.subheader(f"Monthly Profit Comparison by Category ({selected_year})")  
bar_data = (
    df_year
    .groupby(['Month','Category'])['Profit']
    .sum()
    .reset_index()
)
bar_data['Month'] = pd.Categorical(bar_data['Month'], categories=month_order, ordered=True)  
bar_data = bar_data.sort_values('Month')  

fig_bar = px.bar(
    bar_data,
    x='Month',
    y='Profit',
    color='Category',
    barmode='group',
    labels={'Profit':'Profit ($)','Month':'Month'},
    title="Monthly Profit by Category",
    color_discrete_sequence=base_colors
)
fig_bar.update_layout(
    yaxis={'range':[0, bar_data['Profit'].max() * 1.1]},
    xaxis_title='Month',
    yaxis_title='Profit'
)

st.plotly_chart(fig_bar, use_container_width=True)  

# --- Show Table & Download ---  
st.subheader(f"Profit Table for {selected_year}")  
table = (
    df_year
    .groupby('Month')['Profit']
    .sum()
    .reset_index()
)
table['Month'] = pd.Categorical(table['Month'], categories=month_order, ordered=True)
table = table.sort_values('Month')  

st.dataframe(table)  
csv = table.to_csv(index=False).encode('utf-8')  
st.download_button("Download Table as CSV", csv, f"profit_{selected_year}.csv", "text/csv")
