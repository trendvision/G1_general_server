import warnings
warnings.filterwarnings("ignore")
from IPython.display import Image 
from IPython.core.display import Image, display
from collections import Counter
import pandas as pd
import pymongo
import bson
import matplotlib.pyplot as plt
import matplotlib
from tqdm import tqdm
import re
import random
from itertools import permutations
username = "tagger-admin"
password = "tvaiadmin"
db_client = pymongo.MongoClient('104.198.62.226', username=username,
                                password=password,
                                authSource='tags',
                                authMechanism='SCRAM-SHA-256', port=27017).tags


import pickle
from datetime import datetime
from collections import Counter

def FindTag(tag):
    db = db_client["tweets_pipeline_v2"].find({
        "$or":[
#         {"status": 'deleted'},
#         {"status": 'deleted_from_analytics'},
        {"status": 'graphicone_search'}, 
        {"status": 'graphicone_feed'},
#         {"status": 'pipelined'},
#         {"status": 'validated'}
        ]})
    for i in db:
        try:
            entityTags = []
            entity_prepared = []
            grafeed_confirmed = []
            bert_tags = []
            confirmed_after_validate = []
            if "aws_answer" in i:
                entityTags = [answer["Text"].lower() for answer in i["aws_answer"] if answer["Score"] >= 0.99 and answer["Type"] in ["COMMERCIAL_ITEM","EVENT", "LOCATION", "ORGANIZATION", "PERSON"]]
    #         if "entity_prepared" in i and type(i["entity_prepared"])==list:
    #             entity_prepared = i["entity_prepared"]
            if "grafeed_confirmed" in i and type(i["grafeed_confirmed"])==list:
                grafeed_confirmed = i["grafeed_confirmed"]            
            if "bert_tags" in i and type(i["bert_tags"])==list:
                bert_tags = i["bert_tags"]
            if "confirmed_after_validate" in i and  type(i["confirmed_after_validate"])==list:
                confirmed_after_validate = i["confirmed_after_validate"]


            tags = entityTags+entity_prepared+grafeed_confirmed+bert_tags+confirmed_after_validate
            tags = [row.lower() for row in tags]

            tags = list(set(tags))
            if tag in tags:
                print("ID:",i["_id"])
    #             print(i)
                print("Status", i["status"])
                print(tags)
                if "grafeed_confirmed" in i:
                    print("grafeed_confirmed",grafeed_confirmed)
                print()            
                if "s3_url" in i:
                    display(Image(i["s3_url"], unconfined=True))
                else:
                    display(Image(i["img_urls"], unconfined=True))
                print()
                print()
                print()    
        except Exception as err:
            print(err)


