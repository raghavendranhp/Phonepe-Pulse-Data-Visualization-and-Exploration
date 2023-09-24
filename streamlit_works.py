import streamlit as st
import folium
from streamlit_folium import folium_static as st_folium
import pandas as pd
import geopandas as gpd
import warnings
from mysql_querries import mysql_work
import time
import plotly.express as px
from streamlit_functions import *


warnings.filterwarnings('ignore')

sql_handler = mysql_work()
st.set_page_config(page_title="Phonepe Pulse Data Visualization and Exploration!!!", page_icon="https://img.icons8.com/color/96/phone-pe.png", layout="wide")
st.title("Phonepe Pulse Data Visualization and Exploration")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>', unsafe_allow_html=True)
tabs = st.tabs([":blue[🗃] INDIA-States Data", "📈 INSIGHTS"])
agg_trans_df = sql_handler.get_uniques()

# Content for the Home page
with tabs[0]:
    st.header("INDIA-States Data",divider='rainbow')
    st.write('**:orange[Choose your filter:]**')
    col1, col2= st.columns(2)
    with col1:
        selected_year = st.selectbox(":orange[Select Year]", agg_trans_df['YEAR'].unique())
    with col2:
        selected_quarter = st.selectbox(":orange[Select Quarter]", agg_trans_df['QUARTER'].unique())
    india_data_df = sql_handler.get_india_state_mapdf(selected_year, selected_quarter)
    india_df=india_data_df.copy()
    india_df_process(india_df)
    col3, col4= st.columns(2)
    # Filter the DataFrame based on the year and quarter
    filtered_df = india_df[(india_df['YEAR'] == selected_year ) & (india_df['QUARTER'] == selected_quarter)]

    # Calculate the sum of 'TOTAL_REGISTERED_USERS' for the filtered data
    tot_reg_users_sum = filtered_df['TOTAL_REGISTERED_USERS'].sum()
    tot_app_open_sum=filtered_df['TOTAL_REGISTERED_USERS'].sum()
    tot_trans_amount=filtered_df['TOTAL_AMOUNT'].sum()
    tot_trans_amount=sql_handler.convert_to_crores(tot_trans_amount)
    tot_trans_count=filtered_df['TOTAL_COUNT'].sum()
    with col3:
        st.subheader(f'Total Transaction Details for {selected_year}- Q{selected_quarter}:')
        st.metric('_Total Amount_',tot_trans_amount)
        st.metric('_Total Transactions_',tot_trans_count)
        
    with col4:
        st.subheader(f'Total Users Details for {selected_year}- Q{selected_quarter}:')
        st.metric('_Total Registered Users_',tot_reg_users_sum)
        st.metric('_Total App Opens_',tot_app_open_sum)
    filtered_df1 = india_data_df[(india_data_df['YEAR'] == selected_year ) &(india_data_df['QUARTER'] == selected_quarter)]
    india_data_df_process(india_data_df)
    display_map(india_data_df)
# Insights Page
with tabs[1]:
    st.title("Insights from data")
    question_dict={'What are the common insights of a state ':1,
                   'How the Phonepe performing over period and in different states':2,
                   'How are Transaction amount,Registered Users,Transaction Count are related':3,
                   'What are major Transaction over the year':4,
                   'What are the Average Transactions Insights over State':5,
                   'What are the top 5 districts,state,pincode had done highest transaction amount':6,
                   'What are the least 5 districts,state,pincode had done highest transaction amount':7,
                   'Which states are transferring more money (display in table)' :8,
                   'States having high as well as low transactions amount in a Transaction(limited to 7)':9,
                   'States having high as well as low transactions amount by a User(limited to 7)':10 }
    question=st.selectbox('Select the insight questions from phonepe data',question_dict.keys())
    answer=question_dict.get(question)
    if answer==1:
        input_state=st.selectbox('Select the State for insights',agg_trans_df['MYSQL_STATES'].unique())
        st_df=sql_handler.get_state_insights(input_state)
        bar_df=sql_handler.get_state_insights_bar(input_state)
        pie_df=sql_handler.get_state_insights_donut(input_state)
        bubble_df=sql_handler.get_state_insights_bubble_bar(input_state)
        q1_avgtrans_count_chart(st_df)
        q1_bar_chart(bar_df)
        q1_bubble_bar_chart(bubble_df,input_state)
        col1,col2=st.columns((2))
        with col1:
            q1_pie_chart(pie_df,input_state)
        with col2:
            q1_avgtrans_user_chart(st_df)
    elif answer==2:
        user_df,sta_df=sql_handler.get_nation_deatils()
        display_timeseries_nation(user_df,sta_df)
    elif answer==3:
        year_df=sql_handler.get_relative_insights()
        display_scatter(year_df)
    elif answer==4:
        trans_type_df=sql_handler.get_trans_type_insights()
        display_multi_line_trans_type(trans_type_df)
    elif answer==5:
        state_avgtrans_user_df=sql_handler.get_avgtrans_user_count()
        display_stack_bar(state_avgtrans_user_df)
    elif answer==6:
        dis_trans_df,pin_trans_df=sql_handler.get_top5_districts()
        state_avgtrans_user_df=sql_handler.get_avgtrans_user_count()
        display_top5_state_bar(state_avgtrans_user_df)
        display_top5_district_pin_bar(dis_trans_df,pin_trans_df)
    elif answer==7:
        dis_trans_df,pin_trans_df=sql_handler.get_top5_districts()
        state_avgtrans_user_df=sql_handler.get_avgtrans_user_count()
        display_last5_state_district_pin_bar(state_avgtrans_user_df,dis_trans_df,pin_trans_df)
    elif answer==8:
        state_avgtrans_user_df=sql_handler.get_avgtrans_user_count()
        display_ff_trans_table(state_avgtrans_user_df)
    elif answer==9:
        state_avgtrans_user_df=sql_handler.get_avgtrans_user_count()
        display_avg_trans_top(state_avgtrans_user_df)
        display_avg_trans_least(state_avgtrans_user_df)
    elif answer==10:
        state_avgtrans_user_df=sql_handler.get_avgtrans_user_count()
        display_avg_user_top(state_avgtrans_user_df)
        display_avg_user_least(state_avgtrans_user_df)
        