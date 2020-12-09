from pathlib import Path
import requests
import wget
import re
import pandas as pd
import numpy as np
import csv
import os
from tqdm import tqdm

def get_idx_urls():
    QUARTERS = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
    YEARS = list(range(2019, 2030))
    sec_archive_url = 'https://www.sec.gov/Archives/edgar/full-index'
    idx_urls = [sec_archive_url + "/" + str(y)+ "/" + str(q) + "/" for y in YEARS for q in QUARTERS]
    return idx_urls

def downloadFile(content, local_filename):
    with open(local_filename, 'wb') as f:
        f.write(content)
                
def saveLogs(log, logsPath):
    with open(logsPath, 'a') as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(log)
    return True  

def ConvertIDXFast(fileName):
    df = pd.read_fwf(fileName, sep="\t+", skiprows=10, header=None)
    if len(df.columns) == 5:
        df.columns = ['Company name', 'Form type', 'CIK', 'Date', 'url']
        df['CIK'] = df['CIK'].astype(str)
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    else:
        return None
    
def ConvertIDXSlow(fileName):
    with open(fileName, encoding="ISO-8859-1") as f:
        content = f.readlines()

    content = content[8:]
    content.pop(1)

    raw_doc = []
    for cont in content[1:]:
        raw_doc.append([cont[0:62], cont[62:74], cont[74:86], cont[86:98], cont[98:141]])

    df = pd.DataFrame(raw_doc)    
    df.columns = ['Company name', 'Form type', 'CIK', 'Date', 'url']
    df['CIK'] = df['CIK'].astype(str)
    df['Date'] = pd.to_datetime(df['Date'])
    return df    

def URLReplacing(url):
    url = os.path.join('https://www.sec.gov/Archives/', url)
    url = re.sub(".txt","",url) + '-index.htm'
    return url

def Converter(fileName, fileNPPath):
    df = ConvertIDXFast(fileName)
    if df is None:
        df = ConvertIDXSlow(fileName)
    df["link"] = df["url"].apply(lambda x: URLReplacing(x))
    npArray = df.values
    np.save(fileNPPath, npArray)
    return None

def CheckAndUpdateCompaniesDBs(args):    
    PathToFolder = args["DBpath"]
    logsPath = PathToFolder+"/"+"logs.csv"
    idxPath = PathToFolder+'/'+'idx/'
    npPath = PathToFolder+'/'+'np/'
    if not os.path.exists(PathToFolder):
        os.makedirs(PathToFolder)
    if not os.path.exists(idxPath):
        os.makedirs(idxPath)
    if not os.path.exists(npPath):
        os.makedirs(npPath)        
    if not os.path.exists(logsPath):
        with open(logsPath, 'a') as f:
            writer = csv.writer(f, lineterminator="\n")
            writer.writerow(["FileName","Size"])

    CompiesFilingsList = get_idx_urls()
    
    for urlFilling in CompiesFilingsList:
        logsDF = pd.read_csv(logsPath)    
        requestTOSec = requests.get(urlFilling)
        if requestTOSec.headers['content-type'] != "application/xml":
            dateExtractor = re.search(r'(?P<year>\d{4})/(?P<quarter>QTR\d+)/', urlFilling)
            year, quarter = dateExtractor['year'], dateExtractor['quarter']
            fileIDXPath = idxPath+"company"+"_"+year+"_"+quarter+".idx"
            fileNPPath = npPath+"company"+"_"+year+"_"+quarter+".npy"
            r = requests.get(urlFilling+"company.idx")
            if r.status_code == 200:
                fileContent = r.content
                fileSize = len(fileContent)
                fileSizeLogsDF = logsDF[logsDF["FileName"]==fileIDXPath]["Size"].values
                log = [fileIDXPath, fileSize]
                if len(fileSizeLogsDF) > 0 and str(fileSize) != str(fileSizeLogsDF[0]):
                    print("UPDATE:",year, quarter)
                    logsDF = logsDF[logsDF["FileName"]!=fileIDXPath]
                    logsDF.to_csv(logsPath, sep=",", index=False)
                    downloadFile(fileContent, fileIDXPath)
                    Converter(fileIDXPath, fileNPPath)
                    saveLogs(log, logsPath)
                elif len(fileSizeLogsDF) == 0:
                    print("DOWNLOADING:", year, quarter)
                    downloadFile(fileContent, fileIDXPath)
                    Converter(fileIDXPath, fileNPPath)
                    saveLogs(log, logsPath)
            else:
                print("STATUS CODE:",r.status_code)
        else:
            break
    print("DB UPDATED")
    return None