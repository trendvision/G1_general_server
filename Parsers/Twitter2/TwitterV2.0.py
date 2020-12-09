#!/usr/bin/env python
# coding: utf-8

# In[3]:


import csv
import pandas as pd
from tqdm import tqdm
import tweepy

consumer_key="WtkaMM3Noar9SBgb61gYVMugt"
consumer_secret="c0NpOJzakO10TmkSPYxoGIpKIg7hR96vTkZAdI3SmQSJ4Sb55L"
access_key="908690023804997632-x02y0HId6Gcufc7nWjh1w8m3MoWvdlV"
access_secret="q7mjRiOB7mzJtykbhklHe12sewTuHa5umESwjuaYZ1QAi"
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


# In[5]:


TwittUsersStats = pd.read_excel("twitUsersStats.xlsx")
TwittUsersStats = TwittUsersStats[[0,"Relevancy (1 - yes, 0 - no)"]]
InterestingTwittAccounts = list(TwittUsersStats[TwittUsersStats["Relevancy (1 - yes, 0 - no)"]==1][0].values)


# In[ ]:


def FollowingCollector(api, screenName):
    followingList = []
    for i in tqdm(api.friends_ids(screenName), desc=screenName):
        u = api.get_user(i)
        followingList.append(u.screen_name)
    return followingList


# In[ ]:


with open(r'accs.csv', 'a') as f:
    writer = csv.writer(f)
    InterestingTwittAccountsFollowings = []
    for InterestingTwitt in InterestingTwittAccounts[10:]:
        print(InterestingTwitt)
        InterestingTwittAccountsFollowings = FollowingCollector(api, InterestingTwitt)    
        for InterestingTwit in InterestingTwittAccountsFollowings:
            writer.writerow([InterestingTwit])

