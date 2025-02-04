import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load Data
csv_file = "realvnc_sales_data.csv"
df = pd.read_csv(csv_file)

# Convert Dates
df['Created_Date'] = pd.to_datetime(df['Created_Date'])
df['Closed_Date'] = pd.to_datetime(df['Closed_Date'], errors='coerce')

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard Overview", "Sales Analysis"])

# Sidebar Filters
st.sidebar.header("Filter Data")
region_filter = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
industry_filter = st.sidebar.multiselect("Select Industry", df['Industry'].unique(), default=df['Industry'].unique())
deal_stage_filter = st.sidebar.multiselect("Select Deal Stage", df['Deal_Stage'].unique(), default=['Closed Won'])
plan_filter = st.sidebar.multiselect("Select Plan Type", df['Plan_Type'].unique(), default=df['Plan_Type'].unique())

# Apply Filters
df_filtered = df[
    (df['Region'].isin(region_filter)) &
    (df['Industry'].isin(industry_filter)) &
    (df['Deal_Stage'].isin(deal_stage_filter)) &
    (df['Plan_Type'].isin(plan_filter))
]

if page == "Dashboard Overview":
    st.title("RealVNC Revenue Operations Dashboard")

    # Revenue Over Time
    st.subheader("Revenue Over Time")
    df_filtered['Month'] = df_filtered['Closed_Date'].dt.strftime('%Y-%m')
    revenue_over_time = df_filtered.groupby('Month', as_index=False)['ARR (£)'].sum()
    fig_revenue_time = px.line(revenue_over_time, x='Month', y='ARR (£)', markers=True)
    st.plotly_chart(fig_revenue_time)

    # Sales by Industry
    st.subheader("Sales by Industry")
    fig_industry = px.pie(df_filtered, names='Industry', values='Deal_Size (£)')
    st.plotly_chart(fig_industry)

    # Win Rate by Industry
    st.subheader("Win Rate by Industry")
    win_rate_industry = df_filtered.groupby('Industry').apply(lambda x: (x['Deal_Stage'] == 'Closed Won').sum() / len(x) * 100).reset_index()
    win_rate_industry.columns = ['Industry', 'Win Rate (%)']
    fig_win_rate = px.bar(win_rate_industry, x='Industry', y='Win Rate (%)', color='Industry')
    st.plotly_chart(fig_win_rate)

    # ARR Contribution by Plan Type
    st.subheader("ARR Contribution by Plan Type")
    arr_plan = df_filtered.groupby('Plan_Type')['ARR (£)'].sum().reset_index()
    fig_arr_plan = px.bar(arr_plan, x='Plan_Type', y='ARR (£)', color='Plan_Type')
    st.plotly_chart(fig_arr_plan)

    # Closed Won vs Closed Lost Analysis
    st.subheader("Closed Won vs Closed Lost Analysis")
    deal_stage_summary = df_filtered[df_filtered['Deal_Stage'].isin(['Closed Won', 'Closed Lost'])].groupby(['Deal_Stage', 'Industry']).size().reset_index(name='Count')
    fig_closed_analysis = px.bar(deal_stage_summary, x='Deal_Stage', y='Count', color='Industry', barmode='stack')
    st.plotly_chart(fig_closed_analysis)

elif page == "Sales Analysis":
    st.title("Sales Analysis")

    # Average Sales Cycle by Deal Stage
    st.subheader("Average Sales Cycle by Deal Stage")
    sales_cycle_stage = df_filtered.groupby('Deal_Stage')['Sales_Cycle_Days'].mean().reset_index()
    fig_sales_cycle = px.bar(sales_cycle_stage, x='Deal_Stage', y='Sales_Cycle_Days', color='Deal_Stage')
    st.plotly_chart(fig_sales_cycle)

    # Sales Data Summary by Salesperson
    st.subheader("Sales Data Summary by Salesperson")
    df_grouped = df_filtered.groupby('Salesperson_Name').agg(
        TotalDeals=('Opportunity_ID', 'count'),
        TotalPipelineValue=('Deal_Size (£)', 'sum'),
        ClosedWonRevenue=('ARR (£)', lambda x: x[df_filtered['Deal_Stage'] == 'Closed Won'].sum()),
        AverageDealSize=('Deal_Size (£)', 'mean')
    ).reset_index()

    # Rename columns for readability
    df_grouped.columns = ['Salesperson', 'Total Deals', 'Total Pipeline Value (£)', 'Closed Won Revenue (£)', 'Average Deal Size (£)']

    st.write("Click on the column headers to sort the data ascending/descending.")
    st.dataframe(df_grouped)
