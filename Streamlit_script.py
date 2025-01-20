import boto3
import pandas as pd
from io import StringIO
import streamlit as st
import os

st.set_page_config(page_title="Top 5 Stocks", layout="wide")

def get_data():

  s3 = boto3.client('s3')
  
  response = s3.get_object(Bucket = 'stocksectordata' , Key = 'sector_list.txt')
  sector_string = response['Body'].read().decode('utf-8')
  
  sector_list = sector_string.split(', ')
  print(sector_list)
  
  data_response = s3.get_object(Bucket = 'stocksectordata', Key = f'{sector_list[0]}/Data/stock_1.csv')
  data = data_response['Body'].read().decode('utf-8')
  
  df = pd.read_csv(StringIO(data))
  return df.head(2)


st.write(get_data())







