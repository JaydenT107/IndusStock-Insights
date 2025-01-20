import boto3
import pandas as pd
from io import StringIO
import streamlit as st
import os

st.set_page_config(page_title="Top 5 Stocks", layout="wide")

def get_data():
  aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
  aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")
  s3 = boto3.client('s3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name = 'us-east-2')
  
  response = s3.get_object(Bucket = 'stocksectordata' , Key = 'sector_list.txt')
  sector_string = response['Body'].read().decode('utf-8')
  
  sector_list = sector_string.split(', ')
  print(sector_list)
  
  data_response = s3.get_object(Bucket = 'stocksectordata', Key = f'{sector_list[0]}/Data/stock_1.csv')
  data = data_response['Body'].read().decode('utf-8')
  
  df = pd.read_csv(StringIO(data))
  return df


aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

if not aws_access_key or not aws_secret_key:
    st.error("AWS credentials are missing. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.")
    







