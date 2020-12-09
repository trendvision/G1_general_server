#!/usr/bin/env python
# coding: utf-8

# In[3]:


import dropbox


# In[ ]:


def getImages(folder):
    processedData = []
    for image in folder:
        processedData.append(image.name)
    return processedData


# In[ ]:


def getMoreThanCan(folder, dbx):
    images = getImages(folder.entries)
    while True:
        folder = dbx.files_list_folder_continue(folder.cursor)
        images += getImages(folder.entries)
        if not folder.has_more:
            break
    return images


# In[4]:


def getData(path):
    access_token = '7wYL8EDqrSAAAAAAAAAjFKIa8fjneyf3Z6xIHPeK6N09ZyGZrVjY4RZGQPSajNY-'
    timeout = 10.0
    dbx = dropbox.Dropbox(access_token, timeout=timeout)
    response = dbx.files_list_folder(path=path)
    
    processedData = {}
    
    for categories in response.entries:
        
        if categories.name not in processedData:
            processedData[categories.name] = []
            
        folder = dbx.files_list_folder(path=categories.path_lower)
        
        if folder.has_more:
            data = getMoreThanCan(folder, dbx)
            print(categories.name, len(data))
            processedData[categories.name] += data
            
        else:
            data = getImages(folder.entries)
            print(categories.name, len(data))
            processedData[categories.name] += data
            


    print("TOTAL IMAGES PROCESSED:",len(processedData))    
    return processedData



from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd






def ConverData(df):
    tags = df[0]
    mlb = MultiLabelBinarizer()
    Data = (pd.DataFrame(mlb.fit_transform(tags), columns=mlb.classes_, index=df.index))
    return Data

def trashDataForTrainPreprocessing(TrashData, LabelsForTrain):
    TrashDataTraining = {}
    for trashCategory in TrashData:
        if trashCategory in LabelsForTrain:
            TrashDataTraining[trashCategory] = TrashData[trashCategory]

    properData = {}
    for key in TrashDataTraining.keys():
        for _id in TrashDataTraining[key]:
            if _id not in properData:
                properData[_id] = [key]
            else:
                properData[_id] += [key]

    df = pd.DataFrame([properData]).T            
    df.index = [str(row[:-4]) for row in df.index.values]
    
    df = ConverData(df)
    df = df.reset_index()
    df.rename(columns={'index': 'id'}, inplace=True)
    df.set_index("id", inplace=True)
    return df