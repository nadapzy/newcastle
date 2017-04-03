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
    else: df_ua=pd.read_csv('agent_name.csv')
    return df_ua

df_ua=agent_name_from_api(ua_unique,file_name='agent_name.csv')
df=df.merge(df_ua,how='left',left_on='ua',right_index=True)

#calculate risk score for each of the custom_name, define 1% event as risky event
custom_name_pct=df.custom_name.value_counts()/df.custom_name.notnull().sum()
custom_name_score=(custom_name_pct<0.01)*(1/custom_name_pct)
custom_name_score=custom_name_score/max(custom_name_score)*30
df=df.join(custom_name_score,on=['custom_name'],how='left',rsuffix='_score')

#calculate risk score for each of the custom_name, define 1% event as risky event
name_pct=df.name.value_counts()/df.name.notnull().sum()
name_score=(name_pct<0.01)*(1/name_pct)
name_score=name_score/max(name_score)*30
df=df.join(name_score,on=['name'],how='left',rsuffix='_score')

#calculate risk score for each of the browsing 
df.sort_values(by=['device_id','created_at'],ascending=True,inplace=True)
device_grouped=df.groupby(by='device_id')
df['time_diff']=device_grouped.created_at.diff()

df['time_diff_score']=(df.time_diff<df.time_diff.quantile(q=0.02))*(df.time_diff.quantile(q=0.02)-df.time_diff)

df.time_diff_score=df.time_diff_score.fillna(value=0)
df.custom_name_score=df.custom_name_score.fillna(value=0)
df.name_score=df.name_score.fillna(value=0)

df['score']=df.time_diff_score+df.name_score+df.custom_name_score
device_gp=df.groupby(by='device_id')
anomal_device=device_gp.score.sum().sort_values()
print('Here is a list of anomalous device id:')
print(anomal_device[-20:])
