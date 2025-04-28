import streamlit as st
import pandas as pd
import plotly.express as px

# --- App Configuration ---
st.set_page_config(page_title="Sales Dashboard", layout="wide")

# --- Load and Prepare Data ---
@st.cache_data
def load_data():
    df = pd.read_csv('Sales Dataset.csv')
    df['Date'] = pd.to_datetime(df['Year-Month'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.strftime('%b')
    return df

data = load_data()

# State abbreviations for heatmaps
state_abbrev = {
    'Alabama':'AL','Alaska':'AK','Arizona':'AZ','Arkansas':'AR',
    'California':'CA','Colorado':'CO','Connecticut':'CT','Delaware':'DE',
    'Florida':'FL','Georgia':'GA','Hawaii':'HI','Idaho':'ID',
    'Illinois':'IL','Indiana':'IN','Iowa':'IA','Kansas':'KS',
    'Kentucky':'KY','Louisiana':'LA','Maine':'ME','Maryland':'MD',
    'Massachusetts':'MA','Michigan':'MI','Minnesota':'MN','Mississippi':'MS',
    'Missouri':'MO','Montana':'MT','Nebraska':'NE','Nevada':'NV',
    'New Hampshire':'NH','New Jersey':'NJ','New Mexico':'NM','New York':'NY',
    'North Carolina':'NC','North Dakota':'ND','Ohio':'OH','Oklahoma':'OK',
    'Oregon':'OR','Pennsylvania':'PA','Rhode Island':'RI','South Carolina':'SC',
    'South Dakota':'SD','Tennessee':'TN','Texas':'TX','Utah':'UT',
    'Vermont':'VT','Virginia':'VA','Washington':'WA','West Virginia':'WV',
    'Wisconsin':'WI','Wyoming':'WY'
}

# Month order for profit analysis
month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# --- Main Tabs ---
st.title("Sales Dashboard")
heatmap_tab, analysis_tab = st.tabs(["Heatmaps", "Sales Profit Analysis"])

# --- TAB 1: Heatmaps (Quantity & Profit) ---
with heatmap_tab:
    st.header("U.S. Sales Heatmaps")
    all_hp = st.checkbox("View All Categories", key="all_hp")
    col1, col2 = st.columns(2)

    # Quantity Sold
    with col1:
        st.subheader("Quantity Sold by State")
        if all_hp:
            df_qty = data.groupby('State')['Quantity'].sum().reset_index()
            title_q = "Quantity Sold (All Categories)"
        else:
            cat_q = st.selectbox("Category (Qty)", data['Category'].unique(), key="cat_q")
            sub_q = st.selectbox("Sub-Category (Qty)",
                                 data[data['Category']==cat_q]['Sub-Category'].unique(), key="sub_q")
            df_qty = (data[(data['Category']==cat_q)&(data['Sub-Category']==sub_q)]
                      .groupby('State')['Quantity'].sum().reset_index())
            title_q = f"Quantity of {sub_q} Sold"
        df_qty = df_qty[df_qty['State'].isin(state_abbrev)]
        df_qty['Code'] = df_qty['State'].map(state_abbrev)
        fig_q = px.choropleth(
            df_qty,
            locations='Code', locationmode='USA-states',
            color='Quantity', scope='usa',
            color_continuous_scale='YlGnBu',
            title=title_q
        )
        st.plotly_chart(fig_q, use_container_width=True)

    # Profit by State
    with col2:
        st.subheader("Profit by State")
        if all_hp:
            df_prof = data.groupby('State')['Profit'].sum().reset_index()
            title_p = "Profit (All Categories)"
        else:
            cat_p = st.selectbox("Category (Profit)", data['Category'].unique(), key="cat_p")
            sub_p = st.selectbox("Sub-Category (Profit)",
                                 data[data['Category']==cat_p]['Sub-Category'].unique(), key="sub_p")
            df_prof = (data[(data['Category']==cat_p)&(data['Sub-Category']==sub_p)]
                       .groupby('State')['Profit'].sum().reset_index())
            title_p = f"Profit from {sub_p}"
        df_prof = df_prof[df_prof['State'].isin(state_abbrev)]
        df_prof['Code'] = df_prof['State'].map(state_abbrev)
        fig_p = px.choropleth(
            df_prof,
            locations='Code', locationmode='USA-states',
            color='Profit', scope='usa',
            color_continuous_scale='YlOrRd',
            title=title_p
        )
        st.plotly_chart(fig_p, use_container_width=True)

# --- TAB 2: Sales Profit Analysis without sidebar ---
with analysis_tab:
    st.header("Sales Profit Analysis")
    # Layout: filters on left, charts on right
    filter_col, chart_col = st.columns([1, 3])

    # Filters in left column
    with filter_col:
        st.subheader("Filters & Options")
        cats = sorted(data['Category'].unique())
        sel_cats = st.multiselect("Category", cats, default=cats, key='f_cats')
        df_f = data[data['Category'].isin(sel_cats)]
        subs = sorted(df_f['Sub-Category'].unique())
        sel_subs = st.multiselect("Sub-Category", ['All']+subs, default=['All'], key='f_subs')
        if 'All' not in sel_subs:
            df_f = df_f[df_f['Sub-Category'].isin(sel_subs)]
        yrs = sorted(df_f['Year'].unique())
        sel_yrs = st.multiselect("Year(s)", ['All']+[str(y) for y in yrs], default=['All'], key='f_years')
        if 'All' not in sel_yrs:
            df_f = df_f[df_f['Year'].isin([int(y) for y in sel_yrs])]
        line_style = st.selectbox("Line Style", ['Linear','Smooth (Spline)'], key='f_style')
        markers = st.checkbox("Show Markers", True, key='f_markers')

    # Charts in right column
    with chart_col:
        if df_f.empty:
            st.warning("No data for selected filters")
        else:
            # Annual Profit Bar Chart
            st.subheader("Annual Profit by Category")
            yr_bar = df_f.groupby(['Year','Category'])['Profit'].sum().reset_index()
            yr_bar['Year'] = yr_bar['Year'].astype(str)
            yrs_ord = sorted(df_f['Year'].unique())
            fig_bar = px.bar(
                yr_bar, x='Year', y='Profit', color='Category', barmode='group',
                category_orders={'Year':[str(y) for y in yrs_ord]}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

            # Monthly Profit Line Chart
            st.subheader("Monthly Profit Trend")
            grp = 'Category' if 'All' in sel_subs else 'Sub-Category'
            ln_df = df_f.groupby(['Month',grp])['Profit'].sum().reset_index()
            ln_df['Month'] = pd.Categorical(ln_df['Month'], categories=month_order, ordered=True)
            ln_df = ln_df.sort_values('Month')
            fig_line = px.line(
                ln_df, x='Month', y='Profit', color=grp,
                category_orders={'Month':month_order}
            )
            fig_line.update_traces(
                mode='lines+markers' if markers else 'lines',
                line_shape='spline' if line_style=='Smooth (Spline)' else 'linear'
            )
            st.plotly_chart(fig_line, use_container_width=True)

            # Data Table & Download
            st.subheader("Profit Data Table")
            tbl = df_f.groupby(['Year','Month','Category','Sub-Category'])['Profit'].sum().reset_index()
            tbl['Month'] = pd.Categorical(tbl['Month'], categories=month_order, ordered=True)
            tbl = tbl.sort_values(['Year','Month'])
            st.dataframe(tbl)
            st.download_button("Download CSV", tbl.to_csv(index=False).encode(), "sales_profit.csv")
