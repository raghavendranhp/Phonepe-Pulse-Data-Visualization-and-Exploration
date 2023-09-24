import pandas as pd
import os
import json
import mysql.connector
from sqlalchemy import create_engine

# Defining path
path_aggregated_transaction=r"C:\Users\ksund\Music\project_2\pulse-master\pulse-master\data\aggregated\transaction\country\india/state/"
path_aggregated_user=r"C:\Users\ksund\Music\project_2\pulse-master\pulse-master\data\aggregated\user\country\india/state/"
path_map_transaction=r"C:\Users\ksund\Music\project_2\pulse-master\pulse-master\data\map\transaction\hover\country\india/state/"
path_map_user=r"C:\Users\ksund\Music\project_2\pulse-master\pulse-master\data\map\user\hover\country\india/state/"
path_top_transaction=r"C:\Users\ksund\Music\project_2\pulse-master\pulse-master\data\top\transaction\country\india/state/"
path_top_user=r"C:\Users\ksund\Music\project_2\pulse-master\pulse-master\data\top\user\country\india/state/"
# listing directories
state_list_agg_trans=os.listdir(path_aggregated_transaction)
state_list_agg_user=os.listdir(path_aggregated_user)
state_list_map_trans=os.listdir(path_map_transaction)
state_list_map_user=os.listdir(path_map_user)
state_list_top_trans=os.listdir(path_top_transaction)
state_list_top_user=os.listdir(path_top_user)


def load_agg_user_data():
    try:
        agg_user=[]
        for state in state_list_agg_user:
            year_path=path_aggregated_user+state+'/'
            year_list=os.listdir(year_path)
            for year in year_list:
                quarter_path=year_path+year+'/'
                quarter_list=os.listdir(quarter_path)
                for file in quarter_list:
                    file_path=quarter_path+file
                    file_opened=open(file_path,'r')
                    data=json.load(file_opened)
                    if data['data']['usersByDevice'] is None:
                        quarter=int(file.strip('.json'))
                        agg_user.append({
                            'RegisteredUsers':data['data']['aggregated'].get('registeredUsers',0),
                            'App_Opens':data['data']['aggregated'].get('appOpens',0),
                            'Brand':'NA',
                            'Count':0,
                            'Percentage':0,
                            'State':state,
                            'Year':year,
                            'Quarter':quarter
                        })
                    else:   
                        for brand_data in data['data']['usersByDevice']:
                            quarter=int(file.strip('.json'))
                            agg_user.append({
                                'RegisteredUsers':data['data']['aggregated'].get('registeredUsers',0),
                                'App_Opens':data['data']['aggregated'].get('appOpens',0),
                                'Brand':brand_data.get('brand','NA'),
                                'Count':brand_data.get('count',0),
                                'Percentage':brand_data.get('percentage',0),
                                'State':state,
                                'Year':year,
                                'Quarter':quarter
                            })
        agg_user_df=pd.DataFrame(agg_user)
        return agg_user_df
    except Exception as e:
        return None
def load_agg_trans_data():
    try:
        agg_trans=[]
        for state in state_list_agg_trans:
            year_path=path_aggregated_transaction+state+'/'
            year_list=os.listdir(year_path)
            for year in year_list:
                quarter_path=year_path+year+'/'
                quarter_list=os.listdir(quarter_path)
                for file in quarter_list:
                    file_path=quarter_path+file
                    file_opened=open(file_path,'r')
                    data=json.load(file_opened)
                    for payments in data['data']['transactionData']:
                        quarter=int(file.strip('.json'))
                        agg_trans.append({
                            'Transaction_Type':payments['name'],
                            'Count':payments['paymentInstruments'][0].get('count', 0),
                            'Amount':payments['paymentInstruments'][0].get('amount', 0),
                            'State':state,
                            'Year':year,
                            'Quarter':quarter
                        })
        agg_trans_df=pd.DataFrame(agg_trans)
        agg_trans_df['Amount']=agg_trans_df['Amount'].apply(lambda x: round(x,2))
        return agg_trans_df
    except Exception as e:
        return None
def load_map_user_data():
    try:
        map_user=[]
        for state in state_list_map_user:
            year_path=path_map_user+state+'/'
            year_list=os.listdir(year_path)
            for year in year_list:
                quarter_path=year_path+year+'/'
                quarter_list=os.listdir(quarter_path)
                for file in quarter_list:
                    file_path=quarter_path+file
                    file_opened=open(file_path,'r')
                    data=json.load(file_opened)
                    for district, values in data["data"]["hoverData"].items():
                        quarter=int(file.strip('.json'))
                        map_user.append({
                            "District": district if district else 'NA',
                            "RegisteredUsers": values.get("registeredUsers",0),
                            "App_Opens": values.get("appOpens",0),
                            "State":state,
                            "Year":year,
                            "Quarter":quarter
                        })
        map_user_df=pd.DataFrame(map_user)
        return map_user_df
    except Exception as e:
        return None

def load_map_trans_data():
    try:
        map_trans=[]
        for state in state_list_map_trans:
            year_path=path_map_transaction+state+'/'
            year_list=os.listdir(year_path)
            for year in year_list:
                quarter_path=year_path+year+'/'
                quarter_list=os.listdir(quarter_path)
                for file in quarter_list:
                    file_path=quarter_path+file
                    file_opened=open(file_path,'r')
                    data=json.load(file_opened)
                    for entry in data['data']['hoverDataList']:
                        quarter=int(file.strip('.json'))
                        map_trans.append({
                            'District':entry.get('name', 'NA'),
                            'Count':entry['metric'][0].get('count', 0),
                            'Amount':entry['metric'][0].get('amount', 0),
                            'State':state,
                            'Year':year,
                            'Quarter':quarter
                        })
        map_trans_df=pd.DataFrame(map_trans)
        map_trans_df['Amount']=map_trans_df['Amount'].apply(lambda x: round(x,2))
        return map_trans_df
    except Exception as e:
        return None
def load_top_user_data():
    try:   
        top_user_district=[]
        top_user_pincode=[]
        for state in state_list_top_user:
            year_path=path_top_user+state+'/'
            year_list=os.listdir(year_path)
            for year in year_list:
                quarter_path=year_path+year+'/'
                quarter_list=os.listdir(quarter_path)
                for file in quarter_list:
                    file_path=quarter_path+file
                    file_opened=open(file_path,'r')
                    data=json.load(file_opened)
                    for district in data['data']['districts']:
                        quarter=int(file.strip('.json'))
                        top_user_district.append({ 
                            'District':district.get('name','NA'),
                            'RegisteredUsers':district.get('registeredUsers',0),
                            'State':state,
                            'Year':year,
                            'Quarter':quarter
                        })
                    for pincode in data['data']['pincodes']:
                        quarter=int(file.strip('.json'))
                        top_user_pincode.append({ 
                            'Pincode':pincode.get('name','NA'),
                            'RegisteredUsers':pincode.get('registeredUsers',0),
                            'State':state,
                            'Year':year,
                            'Quarter':quarter
                        })
        top_user_district_df=pd.DataFrame(top_user_district)
        top_user_pincode_df=pd.DataFrame(top_user_pincode)
        return top_user_district_df,top_user_pincode_df
    except Exception as e:
        return None,None

def load_top_trans_data():
    try:
        top_trans_district=[]
        top_trans_pincode=[]
        for state in state_list_top_trans:
            year_path=path_top_transaction+state+'/'
            year_list=os.listdir(year_path)
            for year in year_list:
                quarter_path=year_path+year+'/'
                quarter_list=os.listdir(quarter_path)
                for file in quarter_list:
                    file_path=quarter_path+file
                    file_opened=open(file_path,'r')
                    data=json.load(file_opened)
                    for district in data['data']['districts']:
                        quarter=int(file.strip('.json'))
                        top_trans_district.append({
                            'District':district.get('entityName','NA'),
                            'Count':district['metric'].get('count', 0),
                            'Amount':district['metric'].get('amount', 0),
                            'State':state,
                            'Year':year,
                            'Quarter':quarter
                        })
                    
                    for pincode in data['data']['pincodes']:
                        quarter=int(file.strip('.json'))
                        top_trans_pincode.append({
                            'Pincode':pincode.get('entityName','NA'),
                            'Count':pincode['metric'].get('count', 0),
                            'Amount':pincode['metric'].get('amount', 0),
                            'State':state,
                            'Year':year,
                            'Quarter':quarter
                            
                        })
        top_trans_district_df=pd.DataFrame(top_trans_district)
        top_trans_district_df['Amount']=top_trans_district_df['Amount'].apply(lambda x: round(x,2))
        top_trans_pincode_df=pd.DataFrame(top_trans_pincode)
        top_trans_pincode_df['Amount']=top_trans_pincode_df['Amount'].apply(lambda x: round(x,2))
        return top_trans_district_df,top_trans_pincode_df
    except Exception as e:
        return None,None

def load_data_tomysql():
    try:
        connection1 = mysql.connector.connect(
                host='127.0.0.1',
                user='root',
                password='1234',
                database='phonepe_data'
            )
        curs1 = connection1.cursor()
        engine = create_engine('mysql+mysqlconnector://root:1234@127.0.0.1/phonepe_data', echo=True)

        agg_trans_df=load_agg_trans_data()
        map_trans_df=load_map_trans_data()
        top_trans_district_df,top_trans_pincode_df=load_top_trans_data()
        agg_user_df=load_agg_user_data()
        map_user_df=load_map_user_data()
        top_user_district_df,top_user_pincode_df=load_top_user_data()


        agg_trans_df.to_sql("agg_trans", engine, if_exists="replace", index=False)
        map_trans_df.to_sql("map_trans", engine, if_exists="replace", index=False)
        top_trans_district_df.to_sql("top_trans_district", engine, if_exists="replace", index=False)
        top_trans_pincode_df.to_sql("top_trans_pincode", engine, if_exists="replace", index=False)
        agg_user_df.to_sql("agg_user",engine,if_exists="replace",index=False)
        map_user_df.to_sql("map_user",engine,if_exists="replace",index=False)
        top_user_district_df.to_sql("top_user_district",engine,if_exists="replace",index=False)
        top_user_pincode_df.to_sql("top_user_pincode",engine,if_exists="replace",index=False)
        curs1.close()
        connection1.close()
        return 'Data Loaded Sucessfully'
    except Exception as e:
        return e
if __name__ == "__main__":
    load_data_tomysql()