#!/usr/bin/env python
# coding: utf-8

# In[53]:


import boto3
import pandas as pd
from io import StringIO


# In[54]:


region_name = 'us-east-2'
AKI = 'AKIAWNHTHVY2O7RIQH4W'
SAK = 'vPM7QCnSfhsVuJ1oIA8YqZ0rM16vNgjWdTyGgLwt'


# In[55]:


s3 = boto3.client('s3', aws_access_key_id = AKI, aws_secret_access_key = SAK, region_name = region_name)


# In[56]:


response = s3.get_object(Bucket = 'stocksectordata' , Key = 'sector_list.txt')
sector_string = response['Body'].read().decode('utf-8')


# In[57]:


sector_list = sector_string.split(', ')
print(sector_list)


# In[60]:


data_response = s3.get_object(Bucket = 'stocksectordata', Key = f'{sector_list[0]}/Data/stock_1.csv')
data = data_response['Body'].read().decode('utf-8')


# In[61]:


df = pd.read_csv(StringIO(data))


# In[62]:


df


# In[ ]:




