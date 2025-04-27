import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Sales Profit Analysis", layout="wide")

# --- Load Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('Sales Dataset.csv')
    df['Date'] = pd.to_datetime(df['Year-Month'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%b')
    df['YearMonthLabel'] = df['Date'].dt.strftime('%Y-%b')
    return df

data = load_data()

# --- Title ---
st.title("Sales Profit Analysis")

# --- Filters ---
categories = data['Category'].unique()
selected_categories = st.multiselect("Select Category(s)", categories, default=categories)
filtered = data[data['Category'].isin(selected_categories)]

sub_cats = filtered['Sub-Category'].unique()
sub_selected = st.selectbox("Select Sub-Category (Optional)", ['All'] + list(sub_cats))
if sub_selected != 'All':
    filtered = filtered[filtered['Sub-Category'] == sub_selected]

# Year selection (mandatory)
available_years = sorted(filtered['Year'].unique())
year = st.selectbox("Select Year", available_years)
filtered = filtered[filtered['Year'] == year]

# --- Moving Average Smoothing ---
smooth_opt = st.selectbox("Moving Average Smoothing", ['None', '3-month', '6-month'])
filtered_line = (
    filtered.groupby(['Date','YearMonthLabel','Category'])['Profit']
    .sum().reset_index().sort_values('Date')
)
if smooth_opt != 'None':
    w = int(smooth_opt.split('-')[0])
    filtered_line['Profit'] = (
        filtered_line.groupby('Category')['Profit']
        .transform(lambda x: x.rolling(window=w, min_periods=1).mean())
    )

# --- Line Chart Controls ---
line_style = st.selectbox("Line Style", ['Linear', 'Smooth (Spline)'])
show_markers = st.checkbox("Show Markers", value=True)

# --- Line Chart ---
line_fig = px.line(
    filtered_line,
    x='YearMonthLabel', y='Profit', color='Category',
    title='Monthly Profit by Category', labels={'Profit':'Profit ($)','YearMonthLabel':'Month-Year'},
    color_discrete_sequence=px.colors.qualitative.Bold,
    hover_data={'YearMonthLabel':True,'Profit':':,.2f','Category':True}
)
line_fig.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style=='Smooth (Spline)' else 'linear'
)
line_fig.update_layout(
    xaxis={'categoryorder':'array','categoryarray':filtered_line['YearMonthLabel'].unique()},
    yaxis={'range':[0, filtered_line['Profit'].max()*1.1]},
    xaxis_title='Month-Year', yaxis_title='Profit'
)
st.plotly_chart(line_fig, use_container_width=True)

# --- Bar Chart ---
st.subheader("Monthly Profit Comparison by Category (Bar)")
bar_data = (
    filtered.groupby(['YearMonthLabel','Category'])['Profit']
    .sum().reset_index().sort_values('YearMonthLabel')
)
bar_fig = px.bar(
    bar_data,
    x='YearMonthLabel', y='Profit', color='Category', barmode='group',
    title='Monthly Profit by Category', labels={'Profit':'Profit ($)','YearMonthLabel':'Month-Year'},
    color_discrete_sequence=px.colors.qualitative.Bold
)
bar_fig.update_layout(
    xaxis={'categoryorder':'array','categoryarray':bar_data['YearMonthLabel'].unique()},
    yaxis={'range':[0, bar_data['Profit'].max()*1.1]},
    xaxis_title='Month-Year', yaxis_title='Profit'
)
st.plotly_chart(bar_fig, use_container_width=True)

# --- Table & Download ---
st.subheader("Profit Table by Year and Month")
table = (
    filtered.groupby(['Year','Month'])['Profit']
    .sum().reset_index().sort_values(['Year','Month'])
)
st.dataframe(table)
csv = table.to_csv(index=False).encode('utf-8')
st.download_button("Download Table as CSV", csv, "profit_table.csv", "text/csv")
