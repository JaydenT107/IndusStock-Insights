import streamlit as st
import boto3
from io import StringIO
import pandas as pd
import plotly.express as px

col1,col2 = st.columns([3,1])

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

    sector = col2.selectbox('Select Industry', set(sector_list))
  
    tables = []
    names = []
    data_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/AI_analysis.txt')
    AI_description = data_response['Body'].read().decode('utf-8')
    
    for num in range(1,6):
        data_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Data/stock_{num}.csv')
        data = data_response['Body'].read().decode('utf-8')
        name_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Name/stock_{num}_name.txt')
        name = name_response['Body'].read().decode('utf-8')
       
        df = pd.read_csv(StringIO(data))
        tables.append(df)
        names.append(name)
    return [tables,names,sector, AI_description]




def check_color(data):
    if data.iloc[0]['Close'] > data.iloc[-1]['Close']:
        return '#FF2800'
    elif data.iloc[0]['Close'] < data.iloc[-1]['Close']:
        return '#40FF00'
    elif data.iloc[0]['Close'] == data.iloc[-1]['Close']:
        return '#FFFF00'
    
def line_chart(data,name):
    close_min = data['Close'].min()
    close_max = data['Close'].max()
    fig = px.line(data,x = 'Date' , y = 'Close')
    fig.update_yaxes(range=[close_min,close_max])
    fig.update_traces(line = dict(color = check_color(data) ))
    fig.update_xaxes(nticks = 5)
    fig.update_layout(
    title=name,  
    title_x=0.5,            
    title_font=dict(size=24, family='Soin Sans Pro', color='white') 
)
    

    return col1.plotly_chart(fig, use_container_width = True)


def generate_chart():
    data,name,sector,AI_description = get_data()
    if "_" in sector:
        sector = sector.replace("_", " ")
    col1.markdown(f"<h1 style='font-size: 60px; color: white;'>{sector}</h1>", unsafe_allow_html=True)
    col1.write(AI_description)
    for i in range(0,5):
        line_chart(data[i].head(30),name[i])


generate_chart()
