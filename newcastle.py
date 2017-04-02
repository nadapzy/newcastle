# -*- coding: utf-8 -*-
"""
Created on Fri Mar 31 16:48:59 2017

@author: zpeng
"""

import pandas as pd
import datetime
df = pd.read_csv( "castle-event-data-v4.csv",sep=',', header=0, parse_dates=True,quoting=1 )


df_type=df.astype(dtype={'l':'str','continent':'str','country':'str','isp_name':'str'})\
                        .groupby(by=['custom_name','continent','datacenter','proxy','mobile_device'])

df_type.created_at.count().sort_values(ascending=False)

# nunique device / users
df_ua=df.groupby(by='ua')
print(df_ua.created_at.count().sort_values(ascending=False))
#del grouped

#df['device']=df.ua.str.extract(r'\(([\w\s\.]+)[\;\)]')

import requests,os
#ua="MT6735_TD/V1 Linux/3.10.72+ Android/5.1 Release/03.03.2015 Browser/AppleWebKit537.36 Chrome/39.0.0.0 Mobile Safari/537.36 System/Android 5.1"

user_agent={}
ua_unique=df.ua.unique()
file_name='agent_name.csv'
def agent_name_from_api(ua_unique,file_name='agent_name.csv'):
    i=0    
    if not os.path.isfile(file_name):
        for ua in ua_unique:
            if i%500==0:
                print('finishing {0} out of {1} agent'.format(i,len(ua_unique)))
            user_agen_api = requests.get("http://www.useragentstring.com/?uas="+ua+'&getJSON=os_name-agent_name')
            if user_agen_api.status_code==200:
                user_agent[ua]=[user_agen_api.json()['os_name'],user_agen_api.json()['agent_name']]
            i+=1
        df_ua=pd.DataFrame.from_dict(user_agent,orient='index',)
#        df_ua.column=['user_agent']
        df_ua.to_csv('agent_name.csv')

agent_name_from_api(ua_unique,file_name='agent_name.csv')
abc()
df=df.merge(df_ua,how='left',left_on='ua',right_index=True)
df_model=df.drop(['ua','created_at','user_id','session_id','device_id','ip','lon','lat','accuracy'],axis=1)
df_model=df_model.drop(['l'],axis=1)
from sklearn.ensemble import IsolationForest
seed=25
sf=IsolationForest(contamination=0.05,n_jobs=-1,random_state=seed)
# apparently we need to do 1 hot coding for the model

#from sklearn.preprocessing import OneHotEncoder

#enc=OneHotEncoder(categorical_features=[0,1,2,3,4,5,6,10])
df_trans=pd.get_dummies(df_model,dummy_na=True)

sf.fit(df_trans)
df['score']=sf.predict(df_model)
df[df.score==-1].device.value_counts()





