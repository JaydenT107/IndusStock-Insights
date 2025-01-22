import streamlit as st
import boto3
from io import StringIO
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

def date_selectbox():
    period = st.sidebar.selectbox('Select Time Period', ['3 Months', '1 Month', '1 Week'])
    if period == '3 Months':
        return [95,'3_Months_AI_analysis.txt']
    elif period == '1 Month':
        return [31, 'Monthly_AI_analysis.txt']
    elif period == '1 Week':
        return [7, 'Weekly_AI_analysis.txt']

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

    sector = st.sidebar.selectbox('Select Industry', set(sector_list))
  
    tables = []
    names = []
    
    period, AI_description_txt = date_selectbox()

    data_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/AI_Description/{AI_description_txt}')
    AI_description = data_response['Body'].read().decode('utf-8')

    for num in range(1,6):
        data_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Data/stock_{num}.csv')
        data = data_response['Body'].read().decode('utf-8')
        name_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Name/stock_{num}_name.txt')
        name = name_response['Body'].read().decode('utf-8')
       
        df = pd.read_csv(StringIO(data))
        tables.append(df)
        names.append(name)
    return [tables,names,sector, AI_description, period]




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
    

    return st.plotly_chart(fig, use_container_width = True)



def generate_chart():
    col1, col2, col3 = st.columns([3,3,3])
    data,name,sector,AI_description, period = get_data()
    if "_" in sector:
        sector = sector.replace("_", " ")
    with col1:
        st.markdown(f"<h1 style='font-size: 60px; color: white;'>{sector}</h1>", unsafe_allow_html=True)
        st.write(AI_description)
        line_chart(data[3].head(period),name[3])

    with col2:
        for i in range(0,2):
            line_chart(data[i].head(period),name[i])

    with col3:
        for i in range(2,5):
            if i == 3:
                continue
            else:
                line_chart(data[i].head(period),name[i])


generate_chart()
