import streamlit as st
import boto3
from io import StringIO
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide")
st.header('**IndusStock Insight**')
st.write("""IndusStock Insights is an AI-powered platform that helps investors make informed decisions by identifying the top 5 stocks in a specific industry. It pulls real-time data through a stock API and uses advanced machine learning to analyze market trends and company performance.
The platform generates interactive charts and provides intelligent recommendations, guiding users on whether to buy, hold, or avoid stocks based on data-driven insights. With its combination of real-time analysis and AI forecasts, IndusStock Insights empowers users to navigate the stock market confidently and optimize their investments.""")


def date_selectbox():
    end_date = datetime.now()
    period = st.sidebar.selectbox('Select Time Period', ['3 Months', '1 Month', '1 Week'])

    if period == '3 Months':

        start_date = end_date - relativedelta(months=3)
        return [start_date,end_date,'3_Months_AI_analysis.txt', '3 months']

    elif period == '1 Month':

        start_date = end_date - relativedelta(months=1)
        return [start_date,end_date, 'Monthly_AI_analysis.txt', '1 month']

    elif period == '1 Week':

        start_date = end_date - relativedelta(weeks=1)
        return [start_date,end_date, 'Weekly_AI_analysis.txt', '1 week']

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
    
    sday, eday , AI_description_txt, date_format = date_selectbox()

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
    return [tables,names,sector, AI_description, sday,eday, date_format]




def check_color(data):
    if data.iloc[-1]['Close'] > data.iloc[0]['Close']:
        return '#FF2800'
    elif data.iloc[-1]['Close'] < data.iloc[0]['Close']:
        return '#40FF00'
    elif data.iloc[-1]['Close'] == data.iloc[0]['Close']:
        return '#FFFF00'
    
def line_chart(data,name,sday,eday,date_format):
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')
    filtered_data = data[(data['Date'] >= sday) & (data['Date'] <= eday)]
    close_min = filtered_data['Close'].min()
    close_max = filtered_data['Close'].max()
    fig = px.line(filtered_data,x = 'Date' , y = 'Close')
    fig.update_yaxes(range=[close_min,close_max])
    fig.update_traces(x = filtered_data['Date'][::-1], y = filtered_data['Close'][::-1] , line = dict(color = check_color(filtered_data) ))
    fig.update_xaxes(nticks = 5)
    fig.update_layout(
    title=name,  
    title_x=0.5,            
    title_font=dict(size=24, family='Soin Sans Pro', color='white'),
    width = 600,
    height = 400,
    xaxis = dict(tickformat = date_format_func(date_format))
)
    

    return st.plotly_chart(fig, use_container_width = False)

def date_format_func(data):
    if data == '3 months':
        return '%b %Y'
    elif data == '1 month' or '1 week':
        return '%d/%m/%y'

col1, col2, col3 = st.columns([3,3,3])

def generate_chart():
    st.markdown("""<style>.fixed-height {height: 310px;  overflow: auto; }</style>""",unsafe_allow_html=True,)
   
    data,name,sector,AI_description, sday,eday, date_format = get_data()
    if "_" in sector:
        sector = sector.replace("_", " ")
            
    chart_list = []
    with col2:
        
        for i in range(0,2):
            locals()[name[i]] = line_chart(data[i],name[i],sday,eday, date_format)
            chart_list.append(locals()[name[i]])

    with col1:
        st.markdown(f"<h1 style='font-size: 60px; color: white;'>{sector}</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='fixed-height'>{AI_description}</div>",unsafe_allow_html=True)
        locals()[name[3]] = line_chart(data[3],name[3],sday,eday,date_format)
        chart_list.append(locals()[name[3]])        

    with col3:
        for i in range(2,5):
            if i == 3:
                continue
            else:
                locals()[name[i]] = line_chart(data[i],name[i],sday,eday,date_format)
                chart_list.append(locals()[name[i]])
    return name,chart_list     


name,chart_list = generate_chart()
with col1:
    stock_name = st.selectbox('Select Stock',name)

chart_list[chart_list.index(stock_name)]
