import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from tqdm import tqdm
import requests
from lxml.html import fromstring
from csv import writer

tqdm.pandas()


from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType





def driver_chrome(link, PROXY):
    
    options = webdriver.ChromeOptions()
    
    options.add_argument('headless')
    options.add_argument('window-size=1200x600')    
    options.add_argument('--proxy-server=%s' % PROXY)
    driver = webdriver.Chrome(executable_path="1/chromedriver_1", options=options)
    driver.get(link)
    return driver


# In[3]:


def element(driver, XPATH):
    try:    
        element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, XPATH)))
        return element.text
    except TimeoutException as TE:
        return None


# In[93]:


def get_mail(driver):
        
    result_1 = element(driver, '//*[@id="email-finder-form"]/div[2]/div[1]/span')
    result_2 = element(driver, '//*[@id="email-finder-form"]/div[2]/div[2]/div[1]/div/div[2]')
#     result_404 = element(driver, '/html/body/div/div')
    
#     if result_404 is not None and result_404 == '404':
#         return 404
    
    if result_1 is not None:
        return result_1
    
    if result_2 is not None:
        return result_2
    
    else:
        return None


# In[119]:


# def get_proxy_list():
#     r = requests.get("https://www.us-proxy.org/")
# #     r = requests.get("https://free-proxy-list.net/anonymous-proxy.html")
#     soup = BeautifulSoup(r.text)
#     table = soup.find_all("table")[0]
#     df = pd.read_html(str(table))[0]
#     df = df[df["Https"]=="no"]
#     df["Port"] = df["Port"].astype(int).astype(str) 
#     proxies_list = list((df["IP Address"] +":"+ df["Port"]).values)
#     return proxies_list

# def get_proxy_list():
#     url = 'https://free-proxy-list.net/'
#     response = requests.get(url)
#     parser = fromstring(response.text)
#     proxies = set()
#     for i in parser.xpath('//tbody/tr')[:10]:
#         if i.xpath('.//td[7][contains(text(),"yes")]'):
#             #Grabbing IP and corresponding PORT
#             proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
#             proxies.add(proxy)
#     return list(proxies)


# In[120]:


def get_proxy_address(proxies):
    if len(proxies) > 1:
        proxy = proxies[0]
        del proxies[0]
        return proxy
    else:
        return None


# In[121]:


def get_proxy(proxies):
    while True:
        print(len(proxies))
        PROXY = get_proxy_address(proxies)
        if PROXY:
            return PROXY, proxies
            break
        else:
            print("NEW PROXY")
            import downloadProxy
            proxies += list(set(get_proxy_list_a()[:10]))
            proxies += [re.sub("http://|https://","",i) for i in pd.read_csv("proxies.txt", header=None)[0]]+get_proxy_list_b()[:10]
            
    


# In[122]:


def check_acc(link):
    if os.path.exists("accounts.csv"):
        accounts = pd.read_csv("accounts.csv",header=None)
        accounts.columns = ["Full Name", "email", 'website', 'link']
        if link not in accounts.link.values:
            return True


# In[4]:


def append_list_as_row(file_name, list_of_elem):
    # Open file in append mode
    with open(file_name, 'a+', newline='') as write_obj:
        # Create a writer object from csv module
        csv_writer = writer(write_obj)
        # Add contents of list as last row in the csv file
        csv_writer.writerow(list_of_elem)

def get_result(row, PROXY, proxies):    
    link = row["link"]
    website = row["website"]
    name = row["name"]
    email = row["email"]
    if link is not None and check_acc(link) and pd.isnull(email):
        while True:
            print(PROXY, link)
            driver = driver_chrome(link, PROXY)
            email = get_mail(driver)        
            print("EMAIL:",email)
            if email is None or email == "You have reached your free quota. Please create a free account to search more email addresses.":
                print("TimeoutException")
                PROXY, proxies = get_proxy(proxies)            
                driver.close() 
            else:
                print("EMAIL:",email)
                driver.close()
                append_list_as_row('accounts.csv', [name, email, website, link])
                return email
    else:
        return None
        
def get_proxy_list_b():
    r = requests.get("https://www.us-proxy.org/")
    soup = BeautifulSoup(r.text)
    table = soup.find_all("table")[0]
    df = pd.read_html(str(table))[0]
    df = df[df["Https"]=="no"]
    df["Port"] = df["Port"].astype(int).astype(str) 
    proxies_list = list((df["IP Address"] +":"+ df["Port"]).values)
    return proxies_list

def get_proxy_list_a():
    url = 'https://free-proxy-list.net/'
    response = requests.get(url)
    parser = fromstring(response.text)
    proxies = set()
    for i in parser.xpath('//tbody/tr')[:10]:
        if i.xpath('.//td[7][contains(text(),"yes")]'):
            #Grabbing IP and corresponding PORT
            proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
            proxies.add(proxy)
    return list(proxies)

