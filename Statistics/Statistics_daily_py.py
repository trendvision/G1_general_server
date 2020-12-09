import nltk
import warnings
warnings.filterwarnings("ignore")
from IPython.display import Image 
from IPython.core.display import Image, display
from collections import Counter
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
import pymongo
import datetime
# from datetime import datetime, timedelta
import bson
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm
import random
from itertools import permutations
from nltk.tokenize import sent_tokenize, word_tokenize
username = "tagger-admin"
password = "tvaiadmin"
db_client = pymongo.MongoClient('104.198.62.226', username=username,
                                password=password,
                                authSource='tags',
                                authMechanism='SCRAM-SHA-256', port=27017).tags


# import aerospike
# config = {
#     'hosts': [('35.228.136.58', 3000)]
# }
# client = aerospike.client(config).connect()
# data_as_key = ("ids_to_validate", "data", "data")


# # Search & Feed

import csv


# In[9]:



def stats():
    
    
    fields = {datetime.datetime.now():{ "search": db_client["tweets_pipeline_v2"].find({"status": "graphicone_search"}).count(),
                                        "feed": db_client["tweets_pipeline_v2"].find({"status": "graphicone_feed"}).count(),
                                       "total":db_client["tweets_pipeline_v2"].find({"status": "graphicone_search"}).count() + db_client["tweets_pipeline_v2"].find({"status": "graphicone_feed"}).count(),
                                       "pipelined": db_client["tweets_pipeline_v2"].find({"status": "pipelined"}).count(),
                                       "validated": db_client["tweets_pipeline_v2"].find({"status": "validated"}).count(),
                                       "reserved": db_client["tweets_pipeline_v2"].find({"status": "reserved"}).count(),
                                       "trasher": db_client["tweets_pipeline_v2"].find({"status": "trasher"}).count(),
                                       "deleted": db_client["tweets_pipeline_v2"].find({"status": "deleted"}).count(),
                                       "deleted_from_analytics": db_client["tweets_pipeline_v2"].find({"status": "deleted_from_analytics"}).count(),
#                                        "tags:": len(client.get(data_as_key)[-1]['tags'])
                                      }
             }
    with open(r'logs/statistics', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([fields])
    print(fields)
    
    pipeline = [{"$group": {"_id": {
                                    "date":{"$dateToString": { "format": "%Y-%m-%d", "date": "$validated_timestamp" }},
                                    "status": "$status",
                                    }, 
                            "count": {"$sum": 1},
                           }             
                },
               {"$sort": {"_id": -1}}]
    aggregateResults = list(db_client.tweets_pipeline_v2.aggregate(pipeline, allowDiskUse=True))
    counter = 0
    FullDict = {}
    for i in aggregateResults:
        if "status" in i["_id"]:
            if i["_id"]["status"] in ["validated", "deleted", "graphicone_search", "graphicone_feed", "deleted_from_analytics"]:
                counter+=1
                newDict = {}
                newDict["date"] = i["_id"]["date"]
                newDict[i["_id"]["status"]] = i["count"]
                FullDict[counter] = newDict
            
    df = pd.DataFrame.from_dict(FullDict, orient='index').groupby(["date"]).sum().sort_values(by="date", ascending=True)
    df["TOTAL SUM"] = df[[col for col in df.columns]].sum(axis = 1, skipna = True)
    df["APP"] = df["graphicone_search"]+df["graphicone_feed"]
    df["TOTAL DELETED, %"] = (((df["deleted"]+df["deleted_from_analytics"])/(df["TOTAL SUM"]))*100).round(2)
    df["VALIDATOR ERROR, %"] = ((df["deleted_from_analytics"]/(df["APP"]+df["deleted_from_analytics"]))*100).round(2)
    
    colors = ["#EEA04D","#E4D9B5","#a0c8c9","#3F647C","#3F3D50"]
    ax1 = df[['deleted', 'deleted_from_analytics','validated','graphicone_search', 'graphicone_feed']][df.index>="2019-12-02"].plot.bar(stacked=True, color=colors, figsize=(15,7))
#     ax1 = df[['deleted', 'deleted_from_analytics','validated','graphicone_search', 'graphicone_feed']][df.index>="2019-12-02"].plot.bar(stacked=True, figsize=(15,7))
    
    df2 = df[['deleted', 'deleted_from_analytics','validated','graphicone_search', 'graphicone_feed']]
    df2 = df2.div(df2.sum(axis=1), axis=0)*100
    
    ax = df2[df2.index>="2019-12-02"].plot.bar(stacked=True, color=colors, figsize=(15,7))    
    df.to_excel("logs/"+"statsDaily"+str(datetime.datetime.now().date())+".xlsx")
    
    
    df = df.sort_values(by="date", ascending=False)[["graphicone_search", "graphicone_feed"]]
    df = df.reset_index()
    df.date = pd.to_datetime(df.date)
    df_feed = df.groupby('date')["graphicone_feed"].sum().cumsum().reset_index()
    df_feed.set_index('date', inplace=True)
    df_search = df.groupby('date')["graphicone_search"].sum().cumsum().reset_index()
    df_search.set_index('date', inplace=True)
    df_common = df_search.join(df_feed)
    df_common.index = df_common.index.strftime('%Y-%m-%d')
    colors = ["#3F647C","#3F3D50"]
    df_common.plot(kind="bar", figsize=(15,7), color = colors)    
    #2019-12-10 - launch algos
    return df






def UserStats():
#     endDate = datetime.today() 
#     startDate = datetime(2020, 6, 18)
#     'validated_timestamp': {'$gte': endDate, '$lte': startDate}
        
    pipeline = [{"$group": {"_id": {
                                    "date":{"$dateToString": { "format": "%Y-%m-%d", "date": "$validated_timestamp" }},
                                    "status": "$status", 
                                    "validator":"$validator_username",                                
                                    }, 
                            "count": {"$sum": 1},
                            
                           }             
                },


#                {"$sort": {"_id": -1}}
               ]
    aggregateResults = list(db_client.tweets_pipeline_v2.aggregate(pipeline))
    counter = 0
    FullDict = {}
    for i in aggregateResults:
        counter+=1
        if "validator" in i["_id"]:
            if i["_id"]["status"] in ["validated", "deleted", "graphicone_search", "graphicone_feed", "deleted_from_analytics"]:
                newDict = {}
                newDict["date"] = i["_id"]["date"]
                newDict[i["_id"]["status"]] = i["count"]
                newDict["user"] = i["_id"]["validator"]
                FullDict[counter] = newDict
    df = pd.DataFrame.from_dict(FullDict, orient='index').groupby(["date", "user"]).sum().sort_values(by="date", ascending=False)
    df["TOTAL SUM"] = df[[col for col in df.columns]].sum(axis = 1, skipna = True)
    df["APP"] = df["graphicone_search"]+df["graphicone_feed"]
    df["TOTAL DELETED, %"] = (((df["deleted"]+df["deleted_from_analytics"])/(df["TOTAL SUM"]))*100).round(2)
    df["VALIDATOR ERROR, %"] = ((df["deleted_from_analytics"]/(df["APP"]+df["deleted_from_analytics"]))*100).round(2)
    df.to_excel("logs/"+"userStats"+str(datetime.datetime.now().date())+".xlsx")
    return df




def UserStatsAnalyst():
    pipeline = [{"$group": {"_id": {
                                    "date":{"$dateToString": { "format": "%Y-%m-%d", "date": "$approved_timestamp" }},
                                    "status": "$status", 
                                    "validator":"$grafeed_approver",                                
                                    }, 
                            "count": {"$sum": 1},
                           }             
                },


#                {"$sort": {"_id": -1}}
               ]
    aggregateResults = list(db_client.tweets_pipeline_v2.aggregate(pipeline))
    counter = 0
    FullDict = {}
    for i in aggregateResults:
        counter+=1
        if "validator" in i["_id"]:
            if i["_id"]["status"] in ["validated", "deleted", "graphicone_search", "graphicone_feed", "deleted_from_analytics"]:
                newDict = {}
                newDict["date"] = i["_id"]["date"]
                newDict[i["_id"]["status"]] = i["count"]
                newDict["user"] = i["_id"]["validator"]
                FullDict[counter] = newDict
    df = pd.DataFrame.from_dict(FullDict, orient='index').groupby(["date", "user"]).sum().sort_values(by="date", ascending=False)
    df["TOTAL SUM"] = df[[col for col in df.columns]].sum(axis = 1, skipna = True)
    df["APP"] = df["graphicone_search"]+df["graphicone_feed"]
    df["TOTAL DELETED, %"] = (((df["deleted"]+df["deleted_from_analytics"])/(df["TOTAL SUM"]))*100).round(2)
    df["VALIDATOR ERROR, %"] = ((df["deleted_from_analytics"]/(df["APP"]+df["deleted_from_analytics"]))*100).round(2)
    df.to_excel("logs/"+"userStats"+str(datetime.datetime.now().date())+".xlsx")
    return df