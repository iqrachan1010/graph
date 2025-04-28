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

# --- TAB 1: Heatmaps (Quantity & Profit) with separate year filters ---
with heatmap_tab:
    st.header("U.S. Sales Heatmaps")
    all_hp = st.checkbox("View All Categories (applies to both)", key="all_hp")
    col1, col2 = st.columns(2)

    # Quantity Sold
    with col1:
        st.subheader("Quantity Sold by State")
        # Year filter specific to quantity
        years_qty = ['All'] + [str(y) for y in sorted(data['Year'].unique())]
        sel_years_qty = st.selectbox("Year (Qty)", years_qty, key="year_q")
        df_qty = data.copy()
        if sel_years_qty != 'All':
            df_qty = df_qty[df_qty['Year'] == int(sel_years_qty)]

        if all_hp:
            df_plot = df_qty.groupby('State')['Quantity'].sum().reset_index()
            title_q = "Quantity Sold (All Categories)"
        else:
            cat_q = st.selectbox("Category (Qty)", df_qty['Category'].unique(), key="cat_q")
            sub_q = st.selectbox(
                "Sub-Category (Qty)",
                df_qty[df_qty['Category']==cat_q]['Sub-Category'].unique(),
                key="sub_q"
            )
            df_plot = (
                df_qty[(df_qty['Category']==cat_q)&(df_qty['Sub-Category']==sub_q)]
                .groupby('State')['Quantity'].sum().reset_index()
            )
            title_q = f"Quantity of {sub_q} Sold"
        df_plot = df_plot[df_plot['State'].isin(state_abbrev)]
        df_plot['Code'] = df_plot['State'].map(state_abbrev)
        fig_q = px.choropleth(
            df_plot,
            locations='Code', locationmode='USA-states',
            color='Quantity', scope='usa',
            color_continuous_scale='YlGnBu',
            title=title_q
        )
        st.plotly_chart(fig_q, use_container_width=True)

    # Profit by State
    with col2:
        st.subheader("Profit by State")
        # Year filter specific to profit
        years_p = ['All'] + [str(y) for y in sorted(data['Year'].unique())]
        sel_years_p = st.selectbox("Year (Profit)", years_p, key="year_p")
        df_prof = data.copy()
        if sel_years_p != 'All':
            df_prof = df_prof[df_prof['Year'] == int(sel_years_p)]

        if all_hp:
            df_plot = df_prof.groupby('State')['Profit'].sum().reset_index()
            title_p = "Profit (All Categories)"
        else:
            cat_p = st.selectbox("Category (Profit)", df_prof['Category'].unique(), key="cat_p")
            sub_p = st.selectbox(
                "Sub-Category (Profit)",
                df_prof[df_prof['Category']==cat_p]['Sub-Category'].unique(),
                key="sub_p"
            )
            df_plot = (
                df_prof[(df_prof['Category']==cat_p)&(df_prof['Sub-Category']==sub_p)]
                .groupby('State')['Profit'].sum().reset_index()
            )
            title_p = f"Profit from {sub_p}"
        df_plot = df_plot[df_plot['State'].isin(state_abbrev)]
        df_plot['Code'] = df_plot['State'].map(state_abbrev)
        fig_p = px.choropleth(
            df_plot,
            locations='Code', locationmode='USA-states',
            color='Profit', scope='usa',
            color_continuous_scale='YlOrRd',
            title=title_p
        )
        st.plotly_chart(fig_p, use_container_width=True)

# --- TAB 2: Sales Profit Analysis ---
with analysis_tab:
    st.header("Sales Profit Analysis")
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
        yrs2 = sorted(df_f['Year'].unique())
        sel_yrs2 = st.multiselect("Year(s)", ['All']+[str(y) for y in yrs2], default=['All'], key='f_years')
        if 'All' not in sel_yrs2:
            df_f = df_f[df_f['Year'].isin([int(y) for y in sel_yrs2])]
        line_style = st.selectbox("Line Style", ['Linear','Smooth (Spline)'], key='f_style')
        markers = st.checkbox("Show Markers", True, key='f_markers')

    # Charts in right column
    with chart_col:
        if df_f.empty:
            st.warning("No data for selected filters")
        else:
            st.subheader("Annual Profit by Category")
            yr_bar = df_f.groupby(['Year','Category'])['Profit'].sum().reset_index()
            yr_bar['Year'] = yr_bar['Year'].astype(str)
            yrs_ord = sorted(df_f['Year'].unique())
            fig_bar = px.bar(
                yr_bar, x='Year', y='Profit', color='Category', barmode='group',
                category_orders={'Year':[str(y) for y in yrs_ord]}
            )
            st.plotly_chart(fig_bar, use_container_width=True)

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

            st.subheader("Profit Data Table")
            tbl = df_f.groupby(['Year','Month','Category','Sub-Category'])['Profit'].sum().reset_index()
            tbl['Month'] = pd.Categorical(tbl['Month'], categories=month_order, ordered=True)
            tbl = tbl.sort_values(['Year','Month'])
            st.dataframe(tbl)
            st.download_button("Download CSV", tbl.to_csv(index=False).encode(), "sales_profit.csv")
