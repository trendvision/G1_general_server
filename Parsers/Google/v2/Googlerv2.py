import requests
import re
from collections import Counter
import pandas as pd
from bs4 import BeautifulSoup as bs
import os
import json
from tqdm import tqdm
tqdm.pandas()
from itertools import chain
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


def createQueryWords(tag, possible_values): 
    tag = re.sub("&","%26",tag)
#     print("TAG", tag)
    possible_values = [re.sub("&","%26", row) for row in possible_values]
#     print("VALUES", possible_values)
    result = [re.sub(" ","+", tag+" "+row) for row in possible_values]
    return result

def GoogleImageLinksExtractor(QueryWord, startDate, endDate):
    startDay, startMonth, startYear = startDate
    endDay, endMonth, endYear = endDate    
    query = "https://www.google.co.in/search?q="+QueryWord+"&tbas=0&tbs=cdr:1,cd_min:"+str(startMonth)+"/"+str(startDay)+"/"+str(startYear)+",cd_max:"+str(endMonth)+"/"+str(endDay)+"/"+str(endYear)+"&source=lnms&tbm=isch"
    print(query)
    result = bs(requests.get(query,  headers=headers).content, features="lxml")
#     print(query)
    linkCollector = []
    for a in result.find_all("div",{"class":"rg_meta"}):
        try:
            link = json.loads(a.text)["ou"]
            linkCollector.append(link)
        except json.JSONDecodeError as err:
            pass
    print(len(linkCollector))
    return linkCollector



def queryGenerator(tag, startDate, endDate, postFixes): return [row for row in tqdm(set(list(chain.from_iterable([GoogleImageLinksExtractor(query, startDate, endDate) for query in tqdm(createQueryWords(tag, postFixes), postfix=tag)]))))]


def getLinks(startDate, endDate, tagSet, postFixes):
    queryLinkResults = {}
    for tag in tagSet: queryLinkResults[tag] = queryGenerator(tag, startDate, endDate, postFixes)
    return queryLinkResults

####################### DOWNLOADING #############################

def download(url, name, Folder, SubFolder):
    extension = url[-4:]
    r = requests.get(url, timeout=5.0) 
    if extension in [".jpg", ".png"]:        
        directory = os.path.join(Folder, SubFolder)
        if not os.path.exists(directory):
            os.makedirs(directory)
        path = os.path.join(Folder, SubFolder, (str(name) + extension))
        with open(path, 'wb') as f:
            f.write(r.content)       
            
def DownloadLinks(Links, Folder):
    for key in Links:
        counter=0
        for url in tqdm(Links[key], postfix=key):
            counter += 1
            name = counter
            try:
                download(url, name, Folder, key)
            except Exception as err:
#                 print(err)
                pass