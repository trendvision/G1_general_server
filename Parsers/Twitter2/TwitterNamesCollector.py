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


IDs = list(set(list(pd.read_csv("TwitterAccountsIDsCollector.csv",header=None)[0].values)))
IDsfromNames = list(set(list(pd.read_csv("TwitterNamesCollector.csv",header=None)[0].values))) 

with open(r'TwitterNamesCollector.csv', 'a') as f:
    writer = csv.writer(f)
    for ID in tqdm(IDs[:]):
        while True:
            try:
                if ID not in IDsfromNames:
                    screenName = api.get_user(ID).screen_name
                    writer.writerow([ID, screenName])
                break                    
            except Exception as err:
                print(err)
                break
            

