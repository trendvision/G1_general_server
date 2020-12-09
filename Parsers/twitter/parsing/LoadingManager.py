import LoadTweets
import pandas as pd
import os
import time
while True:
	totalLast = 0
	for root, dirs, files in os.walk("../../../DataBase/Raw/Twitter/DB_Twitter_Server/RawMedia"):
    		totalLast += len(files)
    	
	for account in pd.read_csv("accounts.csv", header=None)[0]:
    		LoadTweets.LoadingTweets(account)

	totalNew = 0
	for root, dirs, files in os.walk("../../../DataBase/Raw/Twitter/DB_Twitter_Server/RawMedia"):
    		totalNew += len(files)

	print("TOTAL:",totalNew, " NEW:", totalNew-totalLast)
	time.sleep(21600)
	print("SLEEP 6 HOURS")