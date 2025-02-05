with st.expander("Deal Stage Value Over Time"):
    df_filtered = df_filtered.dropna(subset=['Closed_Date'])
    df_filtered['Month'] = df_filtered['Closed_Date'].dt.to_period('M').dt.to_timestamp()
    revenue_over_time = df_filtered.groupby('Month', as_index=False)['ARR (£)'].sum()
    revenue_over_time['ARR (£)'] = revenue_over_time['ARR (£)'].round(2)
    revenue_over_time['Month'] = revenue_over_time['Month'].dt.strftime('%b, %Y')
    fig_revenue_time = px.line(
        revenue_over_time, x='Month', y='ARR (£)', markers=True,
        labels={"Month": "Time Period", "ARR (£)": "ARR (£)"},
    )
    fig_revenue_time.update_xaxes(
        tickangle=-45, tickmode='array', tickvals=revenue_over_time['Month'][::2]
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
