#!/usr/bin/env python
# coding: utf-8

# In[7]:


import csv
import pandas as pd
from tqdm import tqdm
import tweepy

consumer_key="X6a3LXR3OwERo7E1DdIKKC0Tk"
consumer_secret="1xckS1lOEcj8SyLcMTRnib582iXwigmqZYrBHDusVgObttejCV"
access_key="908690023804997632-HPW3dM7KgzMh0it81mA9hLulz03BjRo"
access_secret="bMROmcs5mKQBtvopW8QIgAr7KGF0IvpJeZhoWK9UtOuzK"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_key, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)


# In[8]:


TwittUsersStats = pd.read_excel("twitUsersStats.xlsx")
TwittUsersStats = TwittUsersStats[[0,"Relevancy (1 - yes, 0 - no)"]]
InterestingTwittAccounts = list(TwittUsersStats[TwittUsersStats["Relevancy (1 - yes, 0 - no)"]==1][0].values)


# In[20]:


def FollowingCollector(api, screenName):
    followingList = []
    Friends = api.friends_ids(screenName)
    return Friends

with open(r'TwitterAccountsIDsCollector.csv', 'a') as f:
    writer = csv.writer(f, delimiter='\n')
    InterestingTwittAccountsFollowings = []
    for InterestingTwitt in tqdm(InterestingTwittAccounts):
        while True:
            try:
                writer.writerow(FollowingCollector(api, InterestingTwitt))    
                break
            except Exception as err:
                print(err)
            