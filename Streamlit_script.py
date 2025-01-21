import streamlit as st
import boto3
from io import StringIO
import pandas as pd
import plotly.express as px

def get_data():
    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets.get("AWS_DEFAULT_REGION", "us-east-2")
    )

    response = s3.get_object(Bucket='stocksectordata', Key='sector_list.txt')
    sector_string = response['Body'].read().decode('utf-8')

    sector_list = sector_string.split(', ')

    data_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector_list[0]}/Data/stock_1.csv')
    data = data_response['Body'].read().decode('utf-8')

    df = pd.read_csv(StringIO(data))
    return df
    
def line_chart():
    data = get_data().head(30)
    fig = px.line(data, 'Date','Close')
    close_min = data['Close'].min()
    close_max = data['Close'].max()
    fig.update_yaxes(range=[close_min,close_max])
    fig.update_xaxes(nticks = 5)

    return st.plotly_chart(fig, use_container_width = True)

line_chart()