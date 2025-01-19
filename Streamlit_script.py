


import boto3
import pandas as pd
from io import StringIO

def get_date():
  s3 = boto3.client('s3', aws_access_key_id = AKI, aws_secret_access_key = SAK, region_name = region_name)
  
  response = s3.get_object(Bucket = 'stocksectordata' , Key = 'sector_list.txt')
  sector_string = response['Body'].read().decode('utf-8')
  
  
  sector_list = sector_string.split(', ')
  print(sector_list)
  
  
  
  data_response = s3.get_object(Bucket = 'stocksectordata', Key = f'{sector_list[0]}/Data/stock_1.csv')
  data = data_response['Body'].read().decode('utf-8')
  
  
  
  
  df = pd.read_csv(StringIO(data))








