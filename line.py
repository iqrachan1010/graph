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

# Extract Year and Month
filtered_data['Year'] = pd.to_datetime(filtered_data['Year-Month']).dt.year
filtered_data['Month'] = pd.to_datetime(filtered_data['Year-Month']).dt.strftime('%b')

# Group by Year, Month, and Category
filtered_data_grouped = filtered_data.groupby(['Year', 'Month', 'Category'])['Profit'].sum().reset_index()

# Year selection placed below filters
selected_year = st.selectbox("Select Year", ['All'] + sorted(filtered_data_grouped['Year'].unique().tolist()))

if selected_year != 'All':
    filtered_data_grouped = filtered_data_grouped[filtered_data_grouped['Year'] == selected_year]

# Pivot data for plotting
pivot_data = filtered_data_grouped.pivot_table(index='Month', columns='Category', values='Profit', fill_value=0)

# Fix month order
month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
filtered_data_grouped['Month'] = pd.Categorical(filtered_data_grouped['Month'], categories=month_order, ordered=True)
filtered_data_grouped = filtered_data_grouped.sort_values('Month')

# Dropdown for line style
line_style = st.selectbox("Select Line Style", ["Linear", "Smooth (Spline)"])

# Checkbox for markers
show_markers = st.checkbox("Show Markers (Dots)", value=True)

# Create interactive fancy chart
fig = px.line(
    filtered_data_grouped,
    x="Month",
    y="Profit",
    color="Category",
    labels={"Profit": "Profit ($)", "Month": "Month"},
    title="Monthly Profit by Category",
    hover_data={
        "Month": True,
        "Profit": ":,.2f",
        "Category": True
    },
    color_discrete_sequence=px.colors.qualitative.Bold
)

# Apply line shape and marker settings
fig.update_traces(
    mode='lines+markers' if show_markers else 'lines',
    line_shape='spline' if line_style == "Smooth (Spline)" else 'linear'
)

# Add annotation for peak month
peak_row = filtered_data_grouped.loc[filtered_data_grouped['Profit'].idxmax()]
fig.add_annotation(
    x=peak_row['Month'],
    y=peak_row['Profit'],
    text=f"🏆 Peak: ${peak_row['Profit']:,.0f}",
    showarrow=True,
    arrowhead=2,
    ax=20,
    ay=-30,
    font=dict(size=12, color="black"),
    bgcolor="yellow",
    bordercolor="black",
    borderwidth=2
)

# Update layout
fig.update_layout(
    yaxis=dict(range=[0, filtered_data_grouped['Profit'].max() * 1.1]),
    xaxis_title="Month",
    yaxis_title="Profit"
)

# Show plot
st.plotly_chart(fig, use_container_width=True)
st.dataframe(pivot_data.reset_index())
