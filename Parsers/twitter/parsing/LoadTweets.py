import tweepy
import csv
import sys
import re
import urllib
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np
import os
import requests
import wget
from urllib.parse import urlparse
from urllib.error import HTTPError
import http.client


def LoadingDataBase(pathToDataBase):
    if os.path.isfile(pathToDataBase) == True:   
        RESULT = np.load(pathToDataBase, allow_pickle=True)
    else:
        RESULT = np.empty((0,5))
    return RESULT


def GetTweets(screen_name, DataBase):
    consumer_key="WtkaMM3Noar9SBgb61gYVMugt"
    consumer_secret="c0NpOJzakO10TmkSPYxoGIpKIg7hR96vTkZAdI3SmQSJ4Sb55L"
    access_key="908690023804997632-x02y0HId6Gcufc7nWjh1w8m3MoWvdlV"
    access_secret="q7mjRiOB7mzJtykbhklHe12sewTuHa5umESwjuaYZ1QAi"
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    try:
        accountIDsList = [int(i) for i in DataBase[np.where(DataBase[:,0] == screen_name)][:,1]]
        if len(accountIDsList) != 0:
            newestID = max(accountIDsList)
        else:
            newestID = None
        
        alltweets = []
        new_tweets = api.user_timeline(screen_name = screen_name, count=1, since_id=newestID)
        if len(new_tweets) != 0:
            alltweets.extend(new_tweets)
            oldestID = alltweets[-1].id - 1
            while len(new_tweets) > 0:
                    new_tweets = api.user_timeline(screen_name = screen_name, count=200, max_id=oldestID, since_id=newestID)
                    alltweets.extend(new_tweets)
                    oldestID = alltweets[-1].id - 1
                    print (screen_name, "%s tweets downloaded" % (len(alltweets)))
            return alltweets
        else:
            return None

    except tweepy.TweepError:
        print("Failed to run the command on that user, Skipping...")


def UpdateDataFrame(screen_name, pathToDataBase):
    DataBase = LoadingDataBase(pathToDataBase)
    alltweets = GetTweets(screen_name, DataBase)
    if alltweets is not None:
        for tweet in alltweets:
            if 'media' in tweet.entities and tweet.id_str not in DataBase:
                DataBase = np.append(DataBase, np.array([[screen_name, 
                                                      tweet.id_str, 
                                                      tweet.created_at, 
                                                      tweet.text.encode("utf-8"), 
                                                      tweet.entities['media'][0]['media_url']]]), axis=0)
        np.save(pathToDataBase, DataBase)
        return "UPDATED"

    
def DownloadingMedia(screen_name, pathToMediaFolder, pathToDataBase):
    DataBase = LoadingDataBase(pathToDataBase)
    DataBaseAccount = [i for i in DataBase[np.where(DataBase[:,0] == screen_name)][:,[1, 4]]]
    for index, media_file in enumerate(DataBaseAccount):
        percentOfDownloaded = ((index+1)/len(DataBaseAccount))*100
        print("DOWNLOADED:", round(percentOfDownloaded,2), "%")
        media_fileID = media_file[0]
        media_fileLink = media_file[1]
        extension = os.path.splitext(urlparse(media_fileLink).path)[1]
        outputFileName = media_fileID + extension
        directory = pathToMediaFolder + "/" + screen_name + '/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        if outputFileName not in os.listdir(directory + '/'):
            output = directory + outputFileName
            try:
                wget.download(media_fileLink, out = output)
            except HTTPError as e:
                print(e)
            except http.client.RemoteDisconnected as e:
                print(e)
    return "DOWNLOADED"
    
    
def LoadingTweets(screen_name):
    pathToMediaFolder = "media"
    pathToDataBase = "TwitteMediaDataBase.npy"
    updatingStatus = UpdateDataFrame(screen_name, pathToDataBase)
    print(updatingStatus)
    downloadingStatus = DownloadingMedia(screen_name, pathToMediaFolder, pathToDataBase)
    print(downloadingStatus)