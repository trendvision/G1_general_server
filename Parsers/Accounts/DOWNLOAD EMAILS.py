import pickle
import pandas as pd
import re
import os


# In[2]:


accounts_clean_data = pd.read_csv("accounts_clean_data.csv")


# In[3]:


import download_py


# In[4]:


from download_py import get_proxy_list_a
from download_py import get_proxy_list_b
from download_py import get_result
import downloadProxy


# In[ ]:





# In[5]:



proxies = [re.sub("http://|https://","",i) for i in pd.read_csv("proxies.txt", header=None)[0]]
proxies += get_proxy_list_a()[:10]

# In[6]:


PROXY, proxies = download_py.get_proxy(proxies)


accounts_clean_data["results"] = accounts_clean_data.progress_apply(lambda x: get_result(x, PROXY, proxies), axis=1)