import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
data = pd.read_csv('Sales Dataset.csv')

# Prepare unique filter options
categories = data['Category'].unique()

# Streamlit UI
st.title("Sales Profit Analysis")

# Smoothing option
smoothing_option = st.selectbox("Apply Moving Average Smoothing?", ["None", "7-month", "30-month"])

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
filtered_data['YearMonthLabel'] = pd.to_datetime(filtered_data['Year-Month']).dt.strftime('%Y-%b')

# Group by Year, YearMonthLabel, and Category
filtered_data_grouped = filtered_data.groupby(['Year', 'YearMonthLabel', 'Category'])['Profit'].sum().reset_index()

# Apply smoothing if selected
if smoothing_option != "None":
    window_size = int(smoothing_option.split('-')[0])
    filtered_data_grouped['Profit'] = (
        filtered_data_grouped
        .groupby('Category')['Profit']
        .transform(lambda x: x.rolling(window=window_size, min_periods=1).mean())
    )

# Year selection placed below filters
selected_year = st.selectbox("Select Year", ['All'] + sorted(filtered_data_grouped['Year'].unique().tolist()))

if selected_year != 'All':
    filtered_data_grouped = filtered_data_grouped[filtered_data_grouped['Year'] == selected_year]

# Dropdown for line style
line_style = st.selectbox("Select Line Style", ["Linear", "Smooth (Spline)"])

# Checkbox for markers
show_markers = st.checkbox("Show Markers (Dots)", value=True)

# Create interactive fancy chart
fig = px.line(
    filtered_data_grouped,
    x="YearMonthLabel",
    y="Profit",
    color="Category",
    labels={"Profit": "Profit ($)", "YearMonthLabel": "Month-Year"},
    title="Monthly Profit by Category",
    hover_data={
        "YearMonthLabel": True,
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

# Define color palette
color_palette = px.colors.qualitative.Bold
categories_in_filtered = filtered_data_grouped['Category'].unique()
category_color_map = dict(zip(categories_in_filtered, color_palette))

# Add peak annotation for each category
for idx, category in enumerate(categories_in_filtered):
    df_category = filtered_data_grouped[filtered_data_grouped['Category'] == category]
    if not df_category.empty:
        peak_row = df_category.loc[df_category['Profit'].idxmax()]
        fig.add_annotation(
            x=peak_row['YearMonthLabel'],
            y=peak_row['Profit'],
            text=f"🏆 {category} Peak: ${peak_row['Profit']:,.0f}",
            showarrow=True,
            arrowhead=2,
            ax=20,
            ay=-30,
            font=dict(size=10, color="black"),
            bgcolor=category_color_map.get(category, "yellow"),
            bordercolor="black",
            borderwidth=1
        )

# Update layout
fig.update_layout(
    yaxis=dict(range=[0, filtered_data_grouped['Profit'].max() * 1.1]),
    xaxis_title="Month-Year",
    yaxis_title="Profit"
)

# Show plot
st.plotly_chart(fig, use_container_width=True)

# Show the data used in the chart
st.dataframe(filtered_data_grouped)
