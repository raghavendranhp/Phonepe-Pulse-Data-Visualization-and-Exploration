import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import locale

class mysql_work():
    connection1 = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='1234',
            database='phonepe_data')
    curs1=connection1.cursor()
    def __init__(self):
        self.connection1 = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='1234',
            database='phonepe_data')
        self.curs1 = self.connection1.cursor()
        self.engine = create_engine('mysql+mysqlconnector://root:1234@127.0.0.1/phonepe_data', echo=True)
       
    def get_uniques(self):
        try:
            aggtrans_query='SELECT transaction_type, state, year, quarter FROM agg_trans WHERE year != 2023'
            aggtrans=[]
            self.curs1.execute(aggtrans_query)
            for details in self.curs1:
                aggtrans.append(details)
            aggtransdf = pd.DataFrame(aggtrans,columns=['TRANSACTION_TYPE','STATE','YEAR','QUARTER'])
            self.curs1.close()
            self.connection1.close()
            aggtransdf['MYSQL_STATES']=aggtransdf['STATE']
            aggtransdf['STATE'] = aggtransdf['STATE'].str.upper()  # Convert to uppercase
            aggtransdf['STATE'] = aggtransdf['STATE'].str.replace('-', ' ')  # Replace '-' with a single space
            aggtransdf['STATE'] = aggtransdf['STATE'].str.replace('&', 'AND')  # Replace '&' with 'AND'
            return aggtransdf
        except Exception as e:
            return None
    def convert_to_crores(self,value):
        locale.setlocale(locale.LC_NUMERIC, 'en_IN')
        value_in_crores = value * 0.00000001  # Conversion factor for crores
        formatted_value = locale.format_string("%.2f", value_in_crores, grouping=True)
        return f"{formatted_value} crores"
    def get_india_state_mapdf(self,selected_year,selected_quarter):
        try:
            query1 = f'''SELECT m.state, m.year,m.quarter,SUM(m.count) AS total_count,SUM(m.amount) AS total_amount,
            SUM(u.registeredusers) AS total_registered_users,SUM(u.app_opens) AS total_app_opens
            FROM map_trans AS m JOIN map_user AS u
            ON m.state = u.state AND m.year = u.year AND m.quarter = u.quarter
            WHERE ((m.year = '{selected_year}') AND (m.quarter = '{selected_quarter}'))
            GROUP BY m.state, m.year, m.quarter
            ORDER BY m.state, m.year, m.quarter;'''
            india_states_maplist = []
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',
            password='1234',
            database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query1)
            for details in curs1:
                india_states_maplist.append(details)
            india_states_mapdf = pd.DataFrame(india_states_maplist,columns=['STATE','YEAR','QUARTER','TOTAL_COUNT','TOTAL_AMOUNT','TOTAL_REGISTERED_USERS','TOTAL_APP_OPENS'])
            india_states_mapdf['STATE'] = india_states_mapdf['STATE'].str.upper()  # Convert to uppercase
            india_states_mapdf['STATE'] = india_states_mapdf['STATE'].str.replace('-', ' ')  # Replace '-' with a single space
            india_states_mapdf['STATE'] = india_states_mapdf['STATE'].str.replace('&', 'AND')  # Replace '&' with 'AND'
            curs1.close()
            connection1.close()
            return india_states_mapdf
        except Exception as e:
            return e
    def get_state_insights(self,input_state):
        try:
            query2 = f"""SELECT at.state,at.year,at.quarter,SUM(at.Count) AS transaction_count,SUM(at.amount) AS transaction_amount,MAX(au.registeredusers) AS registeredusers
                FROM agg_trans AS at LEFT JOIN (SELECT state,year,quarter,MAX(count) AS count,registeredusers FROM agg_user
                WHERE state = '{input_state}' GROUP BY state, year, quarter, registeredusers ) AS au ON at.state = au.state AND at.year = au.year AND at.quarter = au.quarter
                WHERE at.state = '{input_state}' GROUP BY at.state, at.year, at.quarter; """ 
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            out_list=[]
            curs1.execute(query2)
            for details in curs1:
                out_list.append(details)
            out_df=pd.DataFrame(out_list,columns=['STATE','YEAR','QUARTER','TRANSACTION_COUNT','TRANSACTION_AMOUNT','REGISTERED_USERS'])
            out_df['TRANSACTION_COUNT'] = out_df['TRANSACTION_COUNT'].astype(float)
            out_df['REGISTERED_USERS'] = out_df['REGISTERED_USERS'].astype(float)
            out_df['AVG_TRANSACTION_AMOUNT/TRANSACTION'] = out_df['TRANSACTION_AMOUNT'] / out_df['TRANSACTION_COUNT']
            out_df['AVG_TRANSACTION_AMOUNT/USER'] = out_df['TRANSACTION_AMOUNT'] / out_df['REGISTERED_USERS']
            locale.setlocale(locale.LC_NUMERIC, 'en_IN')
            out_df['AVG_TRANSACTION_AMOUNT/TRANSACTION'].apply(lambda x: f'Rs {locale.format_string("%.2f", x, grouping=True)}')
            out_df['AVG_TRANSACTION_AMOUNT/USER'].apply(lambda x: f'Rs {locale.format_string("%.2f", x, grouping=True)}')
            out_df['YEAR-Quarter'] = out_df['YEAR'].astype(str) + '-Q' + out_df['QUARTER'].astype(str)
            curs1.close()
            connection1.close()
            return out_df
        except Exception as e:
            return e
    
    def get_state_insights_bar(self, input_state):
        try:
            query2_bar = f"""SELECT state, brand, sum(count) FROM agg_user WHERE state = '{input_state}' AND year != 2023 GROUP BY state, brand"""
            bar_list = []
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query2_bar)
            for details in curs1:
                bar_list.append(details)
            bar_df = pd.DataFrame(bar_list, columns=['STATE', 'BRAND', 'TRANSACTION_COUNT'])
            
            # Filter out rows where BRAND is 'NA'
            bar_df = bar_df.loc[bar_df['BRAND'] != 'NA'].copy()
            bar_df['TRANSACTION_COUNT'] = bar_df['TRANSACTION_COUNT'].astype(float)
            total_transaction_count = bar_df['TRANSACTION_COUNT'].sum()
            bar_df['Percentage_Users'] = (bar_df['TRANSACTION_COUNT'] * 100) / total_transaction_count
            bar_df['Percentage_Users'] = bar_df['Percentage_Users'].round(2)
            
            # Close cursor but keep the connection open for reuse
            self.curs1.close()
            return bar_df
        except Exception as e:
            return None
    def get_state_insights_donut(self,input_state):
        try:
            query2_pie=f"""SELECT state, Transaction_Type, sum(count) FROM agg_trans WHERE state = '{input_state}' GROUP BY state,Transaction_Type"""
            pie_list=[]
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query2_pie)
            for details in curs1:
                pie_list.append(details)
            pie_df = pd.DataFrame(pie_list, columns=['STATE', 'TRANSACTION_TYPE', 'TRANSACTION_COUNT'])
            pie_df['TRANSACTION_COUNT'] = pie_df['TRANSACTION_COUNT'].astype(float)
            total_transaction_count = pie_df['TRANSACTION_COUNT'].sum()
            pie_df['Percentage_Users'] = (pie_df['TRANSACTION_COUNT'] * 100) / total_transaction_count
            return pie_df
        except Exception as e:
            return e
    def get_state_insights_bubble_bar(self,input_state):
        try:
            query2_bubble=f"""SELECT m.state, m.district, AVG(m.count) as Total_transaction_count, AVG(u.registeredusers) 
            FROM map_trans AS m JOIN map_user AS u ON m.district = u.district WHERE m.state = '{input_state}'
            GROUP BY m.state, m.district"""
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            bubble_list=[]
            curs1.execute(query2_bubble)
            for details in curs1:
                bubble_list.append(details)
            bubble_df=pd.DataFrame(bubble_list,columns=['STATE','DISTRICT','AVG_TRANSACTION_COUNT','AVG_USERS'])
            bubble_df['AVG_USERS'] = pd.to_numeric(bubble_df['AVG_USERS'])
            bubble_df['AVG_TRANSACTION_COUNT'] = pd.to_numeric(bubble_df['AVG_TRANSACTION_COUNT'])
            bubble_df['AVG_TRANSACTION_COUNT'] = bubble_df['AVG_TRANSACTION_COUNT']
            return bubble_df
        except Exception as e:
            return None
    def get_nation_deatils(self):
        try:
            query3="""SELECT year,quarter,sum(registeredusers) as total_users FROM map_user GROUP BY year,quarter;"""
            query4="""SELECT state, year, SUM(registeredusers) AS total_users FROM map_user WHERE
            year = 2018 OR year = 2023 GROUP BY state,year;"""
            user_list=[];sta_list=[]
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query3)
            for details in curs1:
                user_list.append(details)
            user_df=pd.DataFrame(user_list,columns=['YEAR','QUARTER','REGISTERED_USERS'])
            user_df['REGISTERED_USERS']=user_df['REGISTERED_USERS'].astype(int)
            user_df['USERS_ADDED'] = user_df['REGISTERED_USERS'].diff()
            user_df['YEAR-Quarter'] = user_df['YEAR'].astype(str) + '-Q' + user_df['QUARTER'].astype(str)
            curs1.execute(query4)
            for details in curs1:
                sta_list.append(details)
            sta_df=pd.DataFrame(sta_list,columns=['STATE','YEAR','REGISTERED_USERS'])
            sta_df['REGISTERED_USERS']=sta_df['REGISTERED_USERS'].astype(int)
            sta_df['YEAR']=sta_df['YEAR'].astype(int)
            return user_df,sta_df
        except Exception:
            return None
    def get_relative_insights(self):
        try:
            query5="""SELECT at.year,at.quarter,SUM(at.Count) AS transaction_count,
            SUM(at.amount) AS transaction_amount,MAX(au.registeredusers) AS registeredusers
            FROM agg_trans AS at LEFT JOIN (SELECT year,quarter,MAX(count) AS count,registeredusers
            FROM agg_user WHERE year != 2023 GROUP BY year,quarter,registeredusers) AS au 
            ON  at.year = au.year AND at.quarter = au.quarter
            WHERE at.year != 2023 GROUP BY at.year,at.quarter;"""
            year_list=[]
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query5)
            for details in curs1:
                year_list.append(details)
            year_df=pd.DataFrame(year_list,columns=['YEAR','QUARTER','TRANSACTION_COUNT','TRANSACTION_AMOUNT','REGISTERED_USERS'])
            year_df['TRANSACTION_COUNT'] = year_df['TRANSACTION_COUNT'].astype(float)
            year_df['REGISTERED_USERS'] = year_df['REGISTERED_USERS'].astype(float)
            return year_df
        except Exception:
            return None 
    def get_trans_type_insights(self):
        try:
            query6="""SELECT transaction_type,sum(count) as Total_count,sum(amount)as Total_amount,year from agg_trans group by transaction_type,year;"""
            tr_list=[]
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query6)
            for details in curs1:
                tr_list.append(details)
            tr_type_df=pd.DataFrame(tr_list,columns=['TRANSACTION_TYPE','TRANSACTION_COUNT','TRANSACTION_AMOUNT','YEAR'])
            return tr_type_df
        except Exception:
            return None
    def get_avgtrans_user_count(self):
        try:
            query7='''SELECT at.state,AVG(at.Count) AS transaction_count,AVG(at.amount) AS transaction_amount,MAX(au.registeredusers) AS registeredusers
            FROM agg_trans AS at LEFT JOIN (SELECT state,MAX(count) AS count,registeredusers FROM agg_user
            WHERE year!=2023 GROUP BY state, registeredusers ) AS au ON at.state = au.state WHERE year!=2023 GROUP BY at.state;'''
            state_trans_list=[]
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query7)
            for details in curs1:
                state_trans_list.append(details)
            state_trans_df=pd.DataFrame(state_trans_list,columns=['STATE','AVG_TRANSACTION_COUNT','AVG_TRANSACTION_AMOUNT','REGISTERED_USERS'])
            state_trans_df['AVG_TRANSACTION_AMOUNT'] = state_trans_df['AVG_TRANSACTION_AMOUNT'].astype(float)
            state_trans_df['AVG_TRANSACTION_COUNT'] = state_trans_df['AVG_TRANSACTION_COUNT'].astype(float)
            state_trans_df['REGISTERED_USERS'] = state_trans_df['REGISTERED_USERS'].astype(float)
            state_trans_df['AVG_TRANSACTION_AMOUNT/TRANSACTION'] = (state_trans_df['AVG_TRANSACTION_AMOUNT'] / state_trans_df['AVG_TRANSACTION_COUNT']).round(2)
            state_trans_df['AVG_TRANSACTION_AMOUNT/USER'] = (state_trans_df['AVG_TRANSACTION_AMOUNT'] / state_trans_df['REGISTERED_USERS']).round(2)
            state_trans_df = state_trans_df.sort_values(by='AVG_TRANSACTION_AMOUNT/USER', ascending=False)
            return state_trans_df
        except Exception:
            return None
    def get_top5_districts(self):
        try:
            query8='''SELECT district,AVG(amount) as AVG_TRANSACTION_AMOUNT ,state FROM map_trans GROUP BY state,district;'''
            query9='''SELECT pincode,AVG(amount) as AVG_TRANSACTION_AMOUNT ,state FROM top_trans_pincode group by state,pincode;'''
            dis_trans_list=[];pin_trans_list=[]
            connection1 = mysql.connector.connect(host='127.0.0.1',user='root',password='1234',database='phonepe_data')
            curs1=connection1.cursor()
            curs1.execute(query8)
            for details in curs1:
                dis_trans_list.append(details)
            dis_trans_df=pd.DataFrame(dis_trans_list,columns=['DISTRICT','AVG_TRANSACTION_AMOUNT(in crores)','STATE'])
            dis_trans_df['AVG_TRANSACTION_AMOUNT(in crores)']=(dis_trans_df['AVG_TRANSACTION_AMOUNT(in crores)'].astype(float)).round(2)
            dis_trans_df['AVG_TRANSACTION_AMOUNT(in crores)']=(dis_trans_df['AVG_TRANSACTION_AMOUNT(in crores)']*0.0000001).round(2)
            curs1.execute(query9)
            for details in curs1:
                pin_trans_list.append(details)
            pin_trans_df=pd.DataFrame(pin_trans_list,columns=['PINCODE','AVG_TRANSACTION_AMOUNT(in crores)','STATE'])
            pin_trans_df['PINCODE']=pin_trans_df['PINCODE'].astype(str)
            pin_trans_df['PINCODE']='PIN-'+pin_trans_df['PINCODE']
            pin_trans_df['AVG_TRANSACTION_AMOUNT(in crores)']=(pin_trans_df['AVG_TRANSACTION_AMOUNT(in crores)'].astype(float)).round(2)
            pin_trans_df['AVG_TRANSACTION_AMOUNT(in crores)']=(pin_trans_df['AVG_TRANSACTION_AMOUNT(in crores)']*0.0000001).round(2)
            return dis_trans_df,pin_trans_df
        except Exception:
            return None