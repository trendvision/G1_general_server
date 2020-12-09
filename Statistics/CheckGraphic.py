
import warnings
warnings.filterwarnings("ignore")
from collections import Counter
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
import pymongo
import bson
import matplotlib.pyplot as plt
import matplotlib
import random
from itertools import permutations
from IPython.display import Image 
from IPython.core.display import Image, display
username = "tagger-admin"
password = "tvaiadmin"
db_client = pymongo.MongoClient('104.198.62.226', username=username,
                                password=password,
                                authSource='tags',
                                authMechanism='SCRAM-SHA-256', port=27017).tags


# In[20]:


def CheckGraphicID(bson_id):
    a = db_client["tweets_pipeline_v2"].find_one({"_id":bson.ObjectId(bson_id)})
    if a is not None:
        print("new collection")
        if "validator_username" in a:
            print(a["validator_username"])
            
#         if "s3_url" in a:
#             print(a['s3_url'])
#             display(Image(a['s3_url'], unconfined=True))
#         else:            
#             print(a["img_urls"])
#             display(Image(a['img_urls'], unconfined=True))
#         print(a)
#         return a
    
  
        print(a["img_urls"])
#         print(a)
        display(Image(a['img_urls'], unconfined=True))        
        return a

    
    else:
        print("old collection")
        a = db_client["crawled_tweets"].find_one({"_id":bson.ObjectId(bson_id)})
        print(a["validator_username"])
        display(Image(a['s3_url'], unconfined=True))
        return a


