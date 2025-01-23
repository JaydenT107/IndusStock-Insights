import streamlit as st
import boto3
from io import StringIO
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta

st.set_page_config(layout="wide")


def date_selectbox():
    end_date = datetime.now()
    period = st.sidebar.selectbox('Select Time Period', ['3 Months', '1 Month', '1 Week'])

    if period == '3 Months':

        start_date = end_date - relativedelta(months=3)
        return [start_date,end_date,'3_Months_AI_analysis.txt']

    elif period == '1 Month':

        start_date = end_date - relativedelta(months=1)
        return [start_date,end_date, 'Monthly_AI_analysis.txt']

    elif period == '1 Week':

        start_date = end_date - relativedelta(weeks=1)
        return [start_date,end_date, 'Weekly_AI_analysis.txt']

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
    
    sday, eday , AI_description_txt = date_selectbox()

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
    return [tables,names,sector, AI_description, sday,eday]




def check_color(data):
    if data.iloc[-1]['Close'] > data.iloc[0]['Close']:
        return '#FF2800'
    elif data.iloc[-1]['Close'] < data.iloc[0]['Close']:
        return '#40FF00'
    elif data.iloc[-1]['Close'] == data.iloc[0]['Close']:
        return '#FFFF00'
    
def line_chart(data,name,sday,eday):
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')
    filtered_data = data[(data['Date'] >= sday) & (data['Date'] <= eday)]
    close_min = data['Close'].min()
    close_max = data['Close'].max()
    fig = px.line(filtered_data,x = 'Date' , y = 'Close')
    fig.update_yaxes(range=[close_min,close_max])
    fig.update_traces(x = filtered_data['Date'][::-1], y = filtered_data['Close'][::-1] , line = dict(color = check_color(filtered_data) ))
    fig.update_xaxes(nticks = 5)
    fig.update_layout(
    title=name,  
    title_x=0.5,            
    title_font=dict(size=24, family='Soin Sans Pro', color='white'),
    width = 600,
    height = 400
)
    

    return st.plotly_chart(fig, use_container_width = False)


def generate_chart():
    st.markdown(
    """
    <style>
    .fixed-height {
        height: 300px;  
        overflow: auto; 
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    col1, col2, col3 = st.columns([3,3,3])
    data,name,sector,AI_description, sday,eday = get_data()
    if "_" in sector:
        sector = sector.replace("_", " ")

    new_string_list = []
    for index,char in enumerate(AI_description.split(' ')):
        if '%' in char:
            new_string_list.append('**' + char + '**')
        else:
            new_string_list.append(char)

    new_string = ' '.join(new_string_list)
            

    with col1:
        st.markdown(f"<h1 style='font-size: 60px; color: white;'>{sector}</h1>", unsafe_allow_html=True)
        st.markdown(f"{new_string})
        st.write(" ")
        line_chart(data[3],name[3],sday,eday)

    with col2:
        
        for i in range(0,2):
            line_chart(data[i],name[i],sday,eday)
            

    with col3:
        for i in range(2,5):
            if i == 3:
                continue
            else:
                line_chart(data[i],name[i],sday,eday)
                


generate_chart()
st.write("abc")