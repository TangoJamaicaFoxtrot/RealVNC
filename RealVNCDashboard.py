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

# Sidebar Filters
st.sidebar.header("Filter Data")
region_filter = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
industry_filter = st.sidebar.multiselect("Select Industry", df['Industry'].unique(), default=df['Industry'].unique())
deal_stage_filter = st.sidebar.multiselect("Select Deal Stage", df['Deal_Stage'].unique(), default=df['Deal_Stage'].unique())
plan_filter = st.sidebar.multiselect("Select Plan Type", df['Plan_Type'].unique(), default=df['Plan_Type'].unique())

# Apply Filters
df_filtered = df[
    (df['Region'].isin(region_filter)) &
    (df['Industry'].isin(industry_filter)) &
    (df['Deal_Stage'].isin(deal_stage_filter)) &
    (df['Plan_Type'].isin(plan_filter))
]

st.title("RealVNC Revenue Operations Dashboard")

# High-Level Overview Metrics
st.subheader("High-Level Overview")
col1, col2, col3 = st.columns(3)
col1.metric("Total Value of Selected Stages (£)", f"{df_filtered['Deal_Size (£)'].sum():,.2f}")
col2.metric("Closed Won Revenue (£)", f"{df_filtered[df_filtered['Deal_Stage'] == 'Closed Won']['ARR (£)'].sum():,.2f}")
win_rate = (len(df_filtered[df_filtered['Deal_Stage'] == 'Closed Won']) / len(df_filtered) * 100) if len(df_filtered) > 0 else 0
col3.metric("Win Rate (%)", f"{win_rate:.2f}%")

# Collapsible Sections
with st.expander("Deal Stage Value Over Time"):
    # Ensure Closed_Date is valid and remove NaT values
    df_filtered = df_filtered.dropna(subset=['Closed_Date'])
    
    # Convert Month to a proper datetime object for sorting
    df_filtered['Month'] = df_filtered['Closed_Date'].dt.to_period('M').dt.to_timestamp()

    # Aggregate ARR by Month
    revenue_over_time = df_filtered.groupby('Month', as_index=False)['ARR (£)'].sum()
    revenue_over_time['ARR (£)'] = revenue_over_time['ARR (£)'].round(2)

    # Ensure missing months are displayed (fill in gaps in the timeline)
    all_months = pd.date_range(start=revenue_over_time['Month'].min(), 
                               end=revenue_over_time['Month'].max(), freq='MS')
    revenue_over_time = revenue_over_time.set_index('Month').reindex(all_months, fill_value=0).reset_index()
    revenue_over_time.rename(columns={'index': 'Month'}, inplace=True)

    # Format Month as "Jan, 2024"
    revenue_over_time['Month'] = revenue_over_time['Month'].dt.strftime('%b, %Y')

    # Plot the updated graph
    fig_revenue_time = px.line(
        revenue_over_time, x='Month', y='ARR (£)', markers=True,
        labels={"Month": "Month, Year", "ARR (£)": "ARR (£)"},
    )

    # Force chronological order
    fig_revenue_time.update_xaxes(
        type='category', 
        categoryorder='array', 
        categoryarray=revenue_over_time['Month']
    )

    st.plotly_chart(fig_revenue_time)


with st.expander("Sales by Industry"):
    fig_industry = px.pie(df_filtered, names='Industry', values='Deal_Size (£)')
    st.plotly_chart(fig_industry)

with st.expander("Win Rate by Industry"):
    win_rate_industry = df_filtered.groupby('Industry').apply(lambda x: (x['Deal_Stage'] == 'Closed Won').sum() / len(x) * 100).reset_index()
    win_rate_industry.columns = ['Industry', 'Win Rate (%)']
    fig_win_rate = px.bar(win_rate_industry, x='Industry', y='Win Rate (%)', color='Industry')
    st.plotly_chart(fig_win_rate)

with st.expander("ARR Contribution by Plan Type"):
    arr_plan = df_filtered.groupby('Plan_Type')['ARR (£)'].sum().reset_index()
    fig_arr_plan = px.bar(arr_plan, x='Plan_Type', y='ARR (£)', color='Plan_Type')
    st.plotly_chart(fig_arr_plan)

with st.expander("Closed Won vs Closed Lost Analysis"):
    deal_stage_summary = df_filtered[df_filtered['Deal_Stage'].isin(['Closed Won', 'Closed Lost'])].groupby(['Deal_Stage', 'Industry']).size().reset_index(name='Count')
    fig_closed_analysis = px.bar(deal_stage_summary, x='Deal_Stage', y='Count', color='Industry', barmode='stack')
    st.plotly_chart(fig_closed_analysis)

with st.expander("Sales Data Summary by Salesperson"):
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
