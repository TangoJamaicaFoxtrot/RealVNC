import streamlit as st
import pandas as pd
import plotly.express as px

csv_file = "realvnc_sales_data.csv"
df = pd.read_csv(csv_file)

df['Created_Date'] = pd.to_datetime(df['Created_Date'])
df['Closed_Date'] = pd.to_datetime(df['Closed_Date'], errors='coerce')

st.sidebar.header("Filter Data")
region_filter = st.sidebar.multiselect("Select Region", df['Region'].unique(), default=df['Region'].unique())
industry_filter = st.sidebar.multiselect("Select Industry", df['Industry'].unique(), default=df['Industry'].unique())
deal_stage_filter = st.sidebar.multiselect("Select Deal Stage", df['Deal_Stage'].unique(), default=['Closed Won'])
plan_filter = st.sidebar.multiselect("Select Plan Type", df['Plan_Type'].unique(), default=df['Plan_Type'].unique())

df_filtered = df[
    (df['Region'].isin(region_filter)) &
    (df['Industry'].isin(industry_filter)) &
    (df['Deal_Stage'].isin(deal_stage_filter)) &
    (df['Plan_Type'].isin(plan_filter))
]

# KPIs
total_pipeline = df_filtered['Deal_Size (£)'].sum()
closed_won_revenue = df_filtered[df_filtered['Deal_Stage'] == 'Closed Won']['ARR (£)'].sum()
win_rate = len(df_filtered[df_filtered['Deal_Stage'] == 'Closed Won']) / len(df_filtered) * 100 if len(df_filtered) > 0 else 0

# Display Metrics
st.title("RealVNC Revenue Operations Dashboard")
st.metric("Total Pipeline Value (£)", f"{total_pipeline:,.2f}")
st.metric("Closed Won Revenue (£)", f"{closed_won_revenue:,.2f}")
st.metric("Win Rate (%)", f"{win_rate:.2f}%")

# Charts
st.subheader("Sales by Region")
fig_region = px.bar(df_filtered, x='Region', y='Deal_Size (£)', color='Industry', barmode='group')
st.plotly_chart(fig_region)

st.subheader("Deal Size Distribution")
fig_deals = px.histogram(df_filtered, x='Deal_Size (£)', nbins=20, color='Plan_Type')
st.plotly_chart(fig_deals)

st.subheader("Sales by Industry")
fig_industry = px.pie(df_filtered, names='Industry', values='Deal_Size (£)')
st.plotly_chart(fig_industry)

# Display Data
st.subheader("Sales Data Table")
st.dataframe(df_filtered)
