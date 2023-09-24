import streamlit as st
import folium
from streamlit_folium import folium_static as st_folium
import pandas as pd
import geopandas as gpd
import warnings
from mysql_querries import mysql_work
import plotly.express as px
import plotly.graph_objects as go
import statsmodels.api as sm
import plotly.figure_factory as ff
sql_handler = mysql_work()
def india_df_process(india_df):
    india_df['TOTAL_REGISTERED_USERS'] = india_df['TOTAL_REGISTERED_USERS'].astype(float)
    india_df['TOTAL_APP_OPENS']=india_df['TOTAL_APP_OPENS'].astype(float)
    india_df['TOTAL_AMOUNT']=india_df['TOTAL_AMOUNT'].astype(float)
    india_df['TOTAL_COUNT']=india_df['TOTAL_COUNT'].astype(float)
    india_df['QUARTER']=india_df['QUARTER'].astype(float)
    india_df['YEAR']=india_df['YEAR'].astype(str)
    india_df['STATE']=india_df['STATE'].astype(str)
def india_data_df_process(india_data_df):
    
    india_data_df['TOTAL_REGISTERED_USERS'] = india_data_df['TOTAL_REGISTERED_USERS'].astype(float)
    india_data_df['TOTAL_APP_OPENS']=india_data_df['TOTAL_APP_OPENS'].astype(float)
    india_data_df['TOTAL_AMOUNT']=india_data_df['TOTAL_AMOUNT'].apply(sql_handler.convert_to_crores)
    india_data_df['TOTAL_AMOUNT']=india_data_df['TOTAL_AMOUNT'].astype(str)
    india_data_df['TOTAL_COUNT']=india_data_df['TOTAL_COUNT'].astype(float)
    india_data_df['QUARTER']=india_data_df['QUARTER'].astype(float)
    india_data_df['YEAR']=india_data_df['YEAR'].astype(str)
    india_data_df['STATE']=india_data_df['STATE'].astype(str)
def display_map(india_data_df):
    india_location = [20.5937, 78.9629]
    map = folium.Map(location=india_location, zoom_start=5, scrollWheelZoom=False, tiles='CartoDB positron')

    # Load a GeoJSON file containing the boundaries of India
    india_geojson_path = r"C:\Users\ksund\Music\project_2\INDIA_STATESeditted.geojson"
   
    # Create the Choropleth layer with data from the merged DataFrame
    choropleth = folium.Choropleth(
            geo_data=india_geojson_path,
            data=india_data_df,
            columns=['STATE', 'TOTAL_REGISTERED_USERS', 'TOTAL_COUNT', 'TOTAL_AMOUNT'],
            key_on='feature.properties.STATE',
            fill_color='YlOrRd',
            fill_opacity=0.7,
            line_opacity=0.4,
            legend_name='Total Registered Users',
            highlight=True,
            name='Total Registered Users'
        )
    choropleth.geojson.add_to(map)
    choropleth.style_function = lambda x: {
            'fillColor': 'transparent' if x['properties']['TOTAL_REGISTERED_USERS'] is None else 'YlOrRd',
            'color': 'cool',
            'fillOpacity': 0.7,
        }
    choropleth.add_to(map)
    
    # Iterate through features and add the fields to properties
    for feature in choropleth.geojson.data['features']:
        state_name = feature['properties']['STATE']
        if state_name in india_data_df['STATE'].tolist():
            row = india_data_df[india_data_df['STATE'] == state_name].iloc[0]
            feature['properties']['TOTAL_REGISTERED_USERS'] = row['TOTAL_REGISTERED_USERS']
            feature['properties']['TOTAL_COUNT'] = row['TOTAL_COUNT']
            feature['properties']['TOTAL_AMOUNT'] = row['TOTAL_AMOUNT']

    # Define a custom tooltip function with custom CSS style
    def custom_tooltip(feature):
        state = feature['properties']['STATE']
        reg_user = feature['properties']['TOTAL_REGISTERED_USERS']
        trans_amt = feature['properties']['TOTAL_AMOUNT']
        trans_count = feature['properties']['TOTAL_COUNT']
        return f"<div class='custom-tooltip' style='font-size: 16px;'>STATE: {state}<br>TOTAL_REGISTERED_USERS: {reg_user}<br>TOTAL_AMOUNT: {trans_amt}<br>TOTAL_COUNT: {trans_count}</div>"

    # Add custom CSS for the tooltip
    

    folium.GeoJsonTooltip(fields=['STATE', 'TOTAL_REGISTERED_USERS', 'TOTAL_AMOUNT', 'TOTAL_COUNT'], labels=True, localize=True, 
                          sticky=True, style="background-color: #c47558;").add_to(choropleth.geojson)   
    # Create a Streamlit Folium component
    st_map = st_folium(map, width=900, height=850)

def q1_avgtrans_user_chart(st_df):
    fig1 = px.line(st_df,x='YEAR-Quarter',y='AVG_TRANSACTION_AMOUNT/USER',title='Average Transaction Amount per User Over Time',
                          labels={'YEAR-Quarter': 'Year-Quarter', 'AVG_TRANSACTION_AMOUNT/USER': 'Avg Transaction Amount/User (Rs)'})
    fig1.update_xaxes(type='category',  tickmode='auto', showgrid=True,gridcolor='gray', showline=True, linecolor='gray' )
    fig1.update_yaxes(showgrid=True,gridcolor='gray',showline=True,linecolor='gray')
    fig1.update_traces(mode='lines+markers', line=dict(width=2), marker=dict(size=8, symbol='circle', line=dict(width=2)))
    fig1.update_layout(plot_bgcolor='white',legend=dict(orientation='h', y=1.05),title_x=0.5,font=dict(family='Arial', size=12))
    st.plotly_chart(fig1, theme='streamlit', use_container_width=True)
def q1_avgtrans_count_chart(st_df):
    fig2 = px.line(st_df,x='YEAR-Quarter',y='AVG_TRANSACTION_AMOUNT/TRANSACTION',title='Average Transaction Amount per Transaction Over Time',
                          labels={'YEAR-Quarter': 'Year-Quarter', 'AVG_TRANSACTION_AMOUNT/TRANSACTION': 'Avg Transaction Amount/Transaction (Rs)'})
    fig2.update_xaxes(type='category',  tickmode='auto', showgrid=True,gridcolor='gray', showline=True, linecolor='gray' )
    fig2.update_yaxes(showgrid=True,gridcolor='gray',showline=True,linecolor='gray')
    fig2.update_traces(mode='lines+markers', line=dict(width=2), marker=dict(size=8, symbol='circle', line=dict(width=2)))
    fig2.update_layout(plot_bgcolor='white',legend=dict(orientation='h', y=1.05),title_x=0.5,font=dict(family='Arial', size=12))
    st.plotly_chart(fig2, theme='streamlit', use_container_width=True)
def q1_bar_chart(bar_df):
    bar_df = bar_df.sort_values(by='Percentage_Users', ascending=False)
    # Create the horizontal bar chart using Plotly Express
    fig3 = px.bar(bar_df, x='Percentage_Users', y='BRAND', text='TRANSACTION_COUNT', orientation='h')
    fig3.update_layout(
        title=f"Percentage Device Users for the {', '.join(bar_df['STATE'].unique())}",
        xaxis_title='Percentage Users',
        yaxis_title='Brand',
        showlegend=True,
        bargap=0.1,  # Adjust the gap between bars
        yaxis_categoryorder='total ascending',   )
    fig3.update_traces(texttemplate='%{text}', textposition='inside')
    st.plotly_chart(fig3, theme='streamlit', use_container_width=True)
def q1_pie_chart(pie_df,input_state):
    fig4 = px.pie(pie_df, values='Percentage_Users', names='TRANSACTION_TYPE', hole=0.4, title=f"Transaction Type in % for {input_state} ")
    st.plotly_chart(fig4, theme=None,use_container_width=True)
def q1_bubble_bar_chart(bubble_df,input_state):
    fig5 = px.scatter(bubble_df, x='DISTRICT', y='AVG_TRANSACTION_COUNT', size='AVG_USERS', title='AVG_TRANSACTION',
                 labels={'DISTRICT': 'District', 'AVG_TRANSACTION_COUNT': 'Avg Transaction Count'},
                 size_max=40)  # Adjust size_max to control bubble size
    fig5.update_traces(text=bubble_df['AVG_USERS'].apply(lambda x: f'{x:.2f} lakhs'))
    fig5.update_xaxes(tickformat=".0s", title_text="District")
    fig5.update_yaxes(tickformat=".0s", title_text="Transaction Count (Crores)")
    fig5.update_traces(marker=dict(line=dict(width=2, color='DarkSlateGrey')), selector=dict(mode='markers'))
    st.plotly_chart(fig5, theme='streamlit',use_container_width=True)
    fig6 = px.bar(bubble_df, x='DISTRICT', y='AVG_TRANSACTION_COUNT', title=f'AVG_TRANSACTION_COUNT of {input_state}',
             labels={'DISTRICT': 'District', 'AVG_TRANSACTION_COUNT': 'Avg Transaction Count'})
    fig6.update_xaxes(title_text="District")
    fig6.update_yaxes(title_text="Avg Transaction Count")
    st.plotly_chart(fig6, theme='streamlit',use_container_width=True)
def display_timeseries_nation(user_df,sta_df):
    fig7 = px.line(user_df, x='YEAR-Quarter', y='USERS_ADDED', title='Users Added Over Time',
    markers=True, line_shape='linear',render_mode='svg',  
    color_discrete_sequence=['blue'])
    # Customize the layout for a more appealing chart
    fig7= px.line(user_df, x='YEAR-Quarter', y='USERS_ADDED', title="INDIA'S Users Added Over Time")
    fig7.update_traces(mode='lines+markers', line=dict(width=2), marker=dict(size=8, symbol='circle', line=dict(width=2)))
    fig7.update_layout(xaxis_title='Year-Quarter',yaxis_title='Users Added',
        xaxis=dict(tickvals=user_df['YEAR-Quarter'].tolist(), tickangle=45),
        yaxis=dict(showgrid=True, zeroline=False),
        legend=dict(title='Legend'),)
    st.plotly_chart(fig7, theme='streamlit',use_container_width=True)
    filtered_df = sta_df[sta_df['YEAR'].isin([2018, 2023])]
    fig8 = go.Figure()
    fig8.add_trace(go.Scatter( x=filtered_df[filtered_df['YEAR'] == 2018]['REGISTERED_USERS'],
            y=filtered_df[filtered_df['YEAR'] == 2018]['STATE'],
            mode='markers',marker=dict(size=16,color="gray", ),text="2018",
            hovertemplate='<b>%{y}</b><br>Registered Users: %{x}<br>Year: 2018',))

    fig8.add_trace(go.Scatter(x=filtered_df[filtered_df['YEAR'] == 2023]['REGISTERED_USERS'],
            y=filtered_df[filtered_df['YEAR'] == 2023]['STATE'],mode='markers',
            marker=dict(size=16,color="lightskyblue", 
            ),text="2023",hovertemplate='<b>%{y}</b><br>Registered Users: %{x}<br>Year: 2023',))

    #lines connecting 2018 and 2023
    for state in filtered_df['STATE'].unique():
        x_values_2018 = filtered_df[(filtered_df['YEAR'] == 2018) & (filtered_df['STATE'] == state)]['REGISTERED_USERS']
        x_values_2023 = filtered_df[(filtered_df['YEAR'] == 2023) & (filtered_df['STATE'] == state)]['REGISTERED_USERS']
        y_value = state
        #Line color
        fig8.add_shape(go.layout.Shape(type="line",x0=x_values_2018.iloc[0],y0=y_value,x1=x_values_2023.iloc[0],
                y1=y_value,line=dict(color="green",width=2,),))
    fig8.update_layout(title='Users Growth For Diferent States',xaxis_title='Registered Users',
        yaxis_title='State',showlegend=False,height=1200, )
    st.plotly_chart(fig8, theme='streamlit',use_container_width=True)
def display_scatter(year_df):
    fig9= px.scatter(year_df, x='REGISTERED_USERS', y='TRANSACTION_AMOUNT', trendline='ols')
    fig9.update_layout(title='REGISTERED_USERS vs. TRANSACTION_AMOUNT')
    st.plotly_chart(fig9, theme='streamlit',use_container_width=True)
    fig10= px.scatter(year_df, x='TRANSACTION_COUNT', y='TRANSACTION_AMOUNT', trendline='ols')
    fig10.update_layout(title='TRANSACTION_COUNT vs. TRANSACTION_AMOUNT')
    st.plotly_chart(fig10, theme='streamlit',use_container_width=True)
def display_multi_line_trans_type(tr_type_df):
    fig11 = px.line(tr_type_df, x='YEAR', y='TRANSACTION_COUNT', color='TRANSACTION_TYPE', 
              title='Transaction Count by Year and Type')
    fig11.update_xaxes(title_text='Year')
    fig11.update_yaxes(title_text='Transaction Count',type='log')
    st.plotly_chart(fig11, theme='streamlit',use_container_width=True)
    fig12 = px.line(tr_type_df, x='YEAR', y='TRANSACTION_AMOUNT', color='TRANSACTION_TYPE', 
                title='Transaction Amount by Year and Type')
    fig12.update_xaxes(title_text='Year')
    fig12.update_yaxes(title_text='Transaction Amount', type='log')
    st.plotly_chart(fig12, theme='streamlit',use_container_width=True)
def display_stack_bar(state_trans_df):
    fig13 = go.Figure()
    fig13.add_trace(go.Bar(x=state_trans_df['AVG_TRANSACTION_AMOUNT/TRANSACTION'],
        y=state_trans_df['STATE'],orientation='h',
        name='AVG_TRANSACTION_AMOUNT/TRANSACTION',marker=dict(color='royalblue')))
    fig13.add_trace(go.Bar(x=state_trans_df['AVG_TRANSACTION_AMOUNT/USER'],
        y=state_trans_df['STATE'],orientation='h',
        name='AVG_TRANSACTION_AMOUNT/USER',marker=dict(color='orange')))
    fig13.update_layout(title='Average Transaction Amount by State',
        xaxis_title='Average Amount',yaxis_title='State',
        barmode='relative',bargap=0.3,height=1400,width=1000)
    st.plotly_chart(fig13, theme='streamlit',use_container_width=True)
def display_top5_state_bar(state_trans_df):
    state_trans_df=state_trans_df.sort_values(by='AVG_TRANSACTION_AMOUNT',ascending=False)
    top_5_states=state_trans_df.head(5)
    fig14 = px.bar(top_5_states,x='STATE',y='AVG_TRANSACTION_AMOUNT',
        color='STATE',title='Top 5 states by AVG_TRANSACTION_AMOUNT (in crores)',
        labels={'STATE': 'STATE', 'AVG_TRANSACTION_AMOUNT': 'AVG Amount (in crores)'},
        hover_name='STATE')
    fig14.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig14, theme='streamlit',use_container_width=True)
def display_top5_district_pin_bar(dis_trans_df,pin_trans_df):
    dis_trans_df = dis_trans_df.sort_values(by='AVG_TRANSACTION_AMOUNT(in crores)', ascending=False)
    #for top 5 districts
    top_5_districts = dis_trans_df.head(5)
    fig15 = px.bar(top_5_districts,x='DISTRICT',y='AVG_TRANSACTION_AMOUNT(in crores)',
        color='STATE',title='Top 5 Districts by AVG_TRANSACTION_AMOUNT (in crores)',
        labels={'DISTRICT': 'District', 'AVG_TRANSACTION_AMOUNT(in crores)': 'AVG Amount (in crores)'},
        hover_name='STATE')
    fig15.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig15, theme='streamlit',use_container_width=True)
    pin_trans_df= pin_trans_df.sort_values(by='AVG_TRANSACTION_AMOUNT(in crores)', ascending=False)
    
    top_5_pin = pin_trans_df.head(5)
    fig16 = px.bar(top_5_pin,x='PINCODE',y='AVG_TRANSACTION_AMOUNT(in crores)',
        color='STATE',title='Top 5 pincodes by AVG_TRANSACTION_AMOUNT (in crores)',
        labels={'PINCODE': 'Pincode', 'AVG_TRANSACTION_AMOUNT(in crores)': 'AVG Amount (in crores)'},
        hover_name='STATE')
    fig16.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig16, theme='streamlit',use_container_width=True)
def display_last5_state_district_pin_bar(state_trans_df,dis_trans_df,pin_trans_df):
    state_trans_df=state_trans_df.sort_values(by='AVG_TRANSACTION_AMOUNT',ascending=True)
    last_5_states=state_trans_df.head(5)
    fig17= px.bar(last_5_states,x='STATE',y='AVG_TRANSACTION_AMOUNT',
        color='STATE',title='Least 5 states by AVG_TRANSACTION_AMOUNT (in crores)',
        labels={'STATE': 'STATE', 'AVG_TRANSACTION_AMOUNT': 'AVG Amount (in crores)'},
        hover_name='STATE')
    fig17.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig17, theme='streamlit',use_container_width=True)
    dis_trans_df = dis_trans_df.sort_values(by='AVG_TRANSACTION_AMOUNT(in crores)', ascending=True)
    #for districts
    last_5_districts = dis_trans_df.head(5)
    fig18 = px.bar(last_5_districts,x='DISTRICT',y='AVG_TRANSACTION_AMOUNT(in crores)',
        color='STATE',title='Least 5 Districts by AVG_TRANSACTION_AMOUNT (in crores)',
        labels={'DISTRICT': 'District', 'AVG_TRANSACTION_AMOUNT(in crores)': 'AVG Amount (in crores)'},
        hover_name='STATE')
    fig18.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig18, theme='streamlit',use_container_width=True)
    #for pincode 
    pin_trans_df= pin_trans_df.sort_values(by='AVG_TRANSACTION_AMOUNT(in crores)', ascending=True)
    last_5_pin = pin_trans_df.head(5)
    fig19 = px.bar(last_5_pin,x='PINCODE',y='AVG_TRANSACTION_AMOUNT(in crores)',
        color='STATE',title='Least 5 pincodes by AVG_TRANSACTION_AMOUNT (in crores)',
        labels={'PINCODE': 'Pincode', 'AVG_TRANSACTION_AMOUNT(in crores)': 'AVG Amount (in crores)'},
        hover_name='STATE')
    fig19.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig19, theme='streamlit',use_container_width=True)
def display_ff_trans_table(state_avgtrans_user_df):
    state_avgtrans_user_df=state_avgtrans_user_df.sort_values(by='AVG_TRANSACTION_AMOUNT',ascending=False)
    state_trans_list=state_avgtrans_user_df.head(20)
    filtered_state_trans_list = state_trans_list[['STATE', 'AVG_TRANSACTION_AMOUNT', 'REGISTERED_USERS']]
    table_data = [filtered_state_trans_list.columns] + filtered_state_trans_list.values.tolist()
    fig20 = ff.create_table(table_data, height_constant=25)
    fig20.update_layout(title='State Transaction Data',margin=dict(l=10, r=10, t=60, b=10),)
    st.plotly_chart(fig20, theme='streamlit',use_container_width=True)
def display_avg_trans_top(state_avgtrans_user_df):
    #top values
    state_avgtrans_user_df=state_avgtrans_user_df.sort_values(by='AVG_TRANSACTION_AMOUNT/TRANSACTION',ascending=False)
    top_avgtrans_df=state_avgtrans_user_df.head(7)
    fig21 = px.bar(top_avgtrans_df,x='STATE',y='AVG_TRANSACTION_AMOUNT/TRANSACTION',
        color='STATE',title='Top 7 State transferring most Amount per Transaction',
        labels={'STATE': 'State', 'AVG_TRANSACTION_AMOUNT/TRANSACTION': 'AVG_TRANSACTION_AMOUNT/TRANSACTION'},
        hover_name='REGISTERED_USERS')
    fig21.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig21, theme='streamlit',use_container_width=True)
def display_avg_trans_least(state_avgtrans_user_df):
    #least values
    state_avgtrans_user_df=state_avgtrans_user_df.sort_values(by='AVG_TRANSACTION_AMOUNT/TRANSACTION',ascending=True)
    last_avgtrans_df=state_avgtrans_user_df.head(7)
    fig22 = px.bar(last_avgtrans_df,x='STATE',y='AVG_TRANSACTION_AMOUNT/TRANSACTION',
        color='STATE',title='Least 7 State doing less Amount of transactions per Transaction',
        labels={'STATE': 'State', 'AVG_TRANSACTION_AMOUNT/TRANSACTION': 'AVG_TRANSACTION_AMOUNT/TRANSACTION'},
        hover_name='REGISTERED_USERS')
    fig22.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig22, theme='streamlit',use_container_width=True)
def display_avg_user_top(state_avgtrans_user_df):
    #top values
    state_avgtrans_user_df=state_avgtrans_user_df.sort_values(by='AVG_TRANSACTION_AMOUNT/USER',ascending=False)
    top_avguser_df=state_avgtrans_user_df.head(7)
    fig23 = px.bar(top_avguser_df,x='STATE',y='AVG_TRANSACTION_AMOUNT/USER',
        color='STATE',title='Top 7 State transferring most Amount based on a user',
        labels={'STATE': 'State', 'AVG_TRANSACTION_AMOUNT/USER': 'AVG_TRANSACTION_AMOUNT/USER'},
        hover_name='REGISTERED_USERS')
    fig23.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig23, theme='streamlit',use_container_width=True)
def display_avg_user_least(state_avgtrans_user_df):
    #least values
    state_avgtrans_user_df=state_avgtrans_user_df.sort_values(by='AVG_TRANSACTION_AMOUNT/USER',ascending=True)
    last_avguser_df=state_avgtrans_user_df.head(7)
    fig24= px.bar(last_avguser_df,x='STATE',y='AVG_TRANSACTION_AMOUNT/USER',
        color='STATE',title='Least 7 State doing less Amount of transactions based on a user',
        labels={'STATE': 'State', 'AVG_TRANSACTION_AMOUNT/USER': 'AVG_TRANSACTION_AMOUNT/USER'},
        hover_name='REGISTERED_USERS')
    fig24.update_traces(texttemplate='%{y:.2f} crores', textposition='outside')
    st.plotly_chart(fig24, theme='streamlit',use_container_width=True)



