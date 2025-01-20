import boto3
import pandas as pd
from io import StringIO
import streamlit as st
import os

st.set_page_config(page_title="Top 5 Stock", layout="wide")

def get_date():
  aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
  aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
  s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)
  
  response = s3.get_object(Bucket = 'stocksectordata' , Key = 'sector_list.txt')
  sector_string = response['Body'].read().decode('utf-8')
  
  sector_list = sector_string.split(', ')
  print(sector_list)
  
  data_response = s3.get_object(Bucket = 'stocksectordata', Key = f'{sector_list[0]}/Data/stock_1.csv')
  data = data_response['Body'].read().decode('utf-8')
  
  df = pd.read_csv(StringIO(data))
  return df

st.dataframe(get_data())







