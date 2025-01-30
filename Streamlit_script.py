import streamlit as st
import boto3
from io import StringIO
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np
import random 
import json
s3client = boto3.client(
    's3',
    aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
    aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
    region_name=st.secrets.get("AWS_DEFAULT_REGION", "us-east-2")
)

st.set_page_config(layout="wide", page_title = "IndusStock Insight")
st.markdown( f"<h1 style='font-size: 45px; color: white;'>IndusStock <span style='color: yellow;'>Insight</span></h1>",  unsafe_allow_html=True)
st.write("""IndusStock Insights is an AI-powered platform that helps investors make informed decisions by identifying the top 5 stocks in a specific industry. It pulls real-time data through a stock API and uses advanced machine learning to analyze market trends and company performance.
The platform generates interactive charts and provides intelligent recommendations, guiding users on whether to buy, hold, or avoid stocks based on data-driven insights. With its combination of real-time analysis and AI forecasts, IndusStock Insights empowers users to navigate the stock market confidently and optimize their investments.""")


def date_selectbox():
    
    end_date = datetime.now()
    period = st.segmented_control('**Select Time Period**', ['1 Year', '6 Months', '3 Months', '1 Month', '1 Week'], selection_mode = 'single', default = '3 Months')


    if period == '1 Week':

        start_date = end_date - relativedelta(weeks=1)
        return start_date,end_date, 0 , '1 Week'

    elif period == '1 Month':

        start_date = end_date - relativedelta(months=1)
        return start_date,end_date, 1 , '1 Month'

    elif period == '3 Months':

        start_date = end_date - relativedelta(months=3)
        return start_date,end_date, 2 , '3 Months'

    elif period == '6 Months':

        start_date = end_date - relativedelta(months = 6)
        return start_date,end_date, 3, '6 Months'

    elif period == '1 Year':

        start_date = end_date - relativedelta(years=1)
        return start_date,end_date, 4 , '1 Year'

    

def get_sector_func(s3 = s3client):
    col1 , col2 = st.columns(2)
    response = s3.get_object(Bucket='stocksectordata', Key='sector_list.txt')
    sector_string = response['Body'].read().decode('utf-8')

    sector_list = sector_string.split(', ')

    tags_sector_list = sector_list.copy()
    tags_sector_list[tags_sector_list.index('Real_Estate')] = 'Real Estate'

    with col1:
        sector = st.selectbox('**Select Sector**', set(tags_sector_list))
        if sector == 'Real Estate':
            sector = 'Real_Estate'

    return sector

sector = get_sector_func()

gsday, geday , period_index , gdate_format = date_selectbox()

def get_data(sday = gsday, eday = geday, period_index = period_index, date_format = gdate_format, sector = sector, s3 = s3client):

    tables = []
    names_list = []
    
    data_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/All_Close_AI_analysis.txt')
    AI_description = data_response['Body'].read().decode('utf-8')
    Display_AI_description = AI_description.split('\n\n')[period_index]
    name_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/name.txt')
    names = name_response['Body'].read().decode('utf-8')
    names = names.split(', ')

    for num in range(1,6):
        data_response = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Data/stock_{num}.csv')
        data = data_response['Body'].read().decode('utf-8') 
        df = pd.read_csv(StringIO(data))

        tables.append(df)
        names_list.append(names[num-1])
    return [tables,names_list,sector, Display_AI_description, sday,eday, date_format]




def check_color(data):
    if data.iloc[-1]['Close'] > data.iloc[0]['Close']:
        return '#FF2800'
    elif data.iloc[-1]['Close'] < data.iloc[0]['Close']:
        return '#40FF00'
    elif data.iloc[-1]['Close'] == data.iloc[0]['Close']:
        return '#FFFF00'
    
def line_chart(data,name,sday,eday,date_format, date_format_2 ,new_title=None, add_trendline = False):
    if name == None:
        name = new_title
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')
    filtered_data = data[(data['Date'] >= sday) & (data['Date'] <= eday)]
    close_min = filtered_data['Close'].min()
    close_max = filtered_data['Close'].max()
    fig = px.line(filtered_data,x = 'Date' , y = 'Close')
    fig.update_yaxes(range=[close_min,close_max], title = None)
    line_color = check_color(filtered_data)
    fig.update_traces(x = filtered_data['Date'][::-1], y = filtered_data['Close'][::-1] , line = dict(color = line_color ))
    fig.update_xaxes(nticks = 5)
    fig.update_layout(
    dragmode = False,
    title=name ,  
    title_x=0.5,            
    title_font=dict(size=24, family='Soin Sans Pro', color='white'),
    width = 600,
    height = 400,
    xaxis = dict(tickformat = date_format_func(date_format))
)
    if add_trendline == True:
        relative_date,relative_title= date_format_func2(date_format_2)
        filtered_data_2 = filtered_data[filtered_data['Date'] >= (datetime.today()-relative_date)]
        line_color_2 = check_color(filtered_data_2)
        line_start_high = filtered_data_2.iloc[0]['High']
        line_end_high = filtered_data_2.iloc[-1]['High']
        line_start_low = filtered_data_2.iloc[0]['Low']
        line_end_low = filtered_data_2.iloc[-1]['Low']
        line_start_date = filtered_data_2.iloc[0]['Date']
        line_start_value = filtered_data_2.iloc[0]['Close']
        line_end_date = filtered_data_2.iloc[-1]['Date']
        line_end_value = filtered_data_2.iloc[-1]['Close']
        random_ax1 = random.randint(-50,50)
        random_ax2 = random.randint(-50,50)
        fig.add_shape(type = 'line', x0 = line_start_date, y0 = line_start_value, x1 = line_end_date, y1 = line_end_value, line = dict(color = line_color_2, width = 2, dash = 'dash'))
        fig.add_shape(type = 'line', x0 = line_start_date, y0 = line_start_high, x1 = line_end_date, y1 = line_end_high, line = dict(color = 'yellow', width = 2, dash = 'dash'))
        fig.add_shape(type = 'line', x0 = line_start_date, y0 = line_start_low, x1 = line_end_date, y1 = line_end_low, line = dict(color = 'yellow', width = 2, dash = 'dash'))
        fig.add_annotation(y = line_start_value, x = line_start_date, showarrow = True, text = f"{line_start_value}", ax = random_ax1 , ay = random_ax2, borderwidth = 0.1, arrowcolor = 'yellow')
        fig.add_annotation(y = line_end_value, x = line_end_date, showarrow = True, text = f"{line_end_value}", ax = random_ax2 , ay = random_ax1, borderwidth = 0.1, arrowcolor = 'yellow')


    return [fig,line_color]

def check_average(average_period,average):
    if average_period > average:
        avg_line_color = '#40FF00'
        return avg_line_color
    else:
        avg_line_color = '#FF2800'
        return avg_line_color


def scatter_plot(data,name,sday,eday,date_format, date_format_2,new_title=None):

    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')
    filtered_data = data[(data['Date'] >= sday) & (data['Date'] <= eday)]
    relative_date,relative_title = date_format_func2(date_format_2)
    filtered_data['Highlight'] = np.where(filtered_data['Date'] >= (datetime.today()-relative_date),relative_title, 'Older')
    filtered_data['Volume_Period'] = np.where(filtered_data['Date'] >= (datetime.today()-relative_date),filtered_data['Volume'], np.nan)

    average_period = filtered_data['Volume_Period'].mean()

    average = filtered_data['Volume'].mean()
    

    avg_line_color = check_average(average_period,average)

    fig = px.scatter(filtered_data, x = 'Close', y = 'Volume', hover_data = ['Date'], color = 'Highlight', color_discrete_map={relative_title: 'red', 'Older': 'light blue'})
    fig.add_hline(y = average, line_dash = 'solid', line_color = 'yellow', name = 'Avg Volume' , showlegend = True)
    fig.add_hline(y = average_period, line_dash = 'dash', line_color = avg_line_color, name = f'Avg Volume: {relative_title}', showlegend = True)
    fig.update_xaxes(title = 'Price')
    fig.update_layout(
    dragmode = False,
    title='Correlation Between Trading Volume and Closing Price',            
    title_font=dict(size=24, family='Soin Sans Pro', color='white'),
    width = 600,
    height = 400,
     legend=dict( x=0,  y=0.98, title = None, borderwidth = 0.3, font = dict(size = 12),bgcolor="rgba(0,0,0,0)")
)

    return fig

def volatility_chart(data,name,sday,eday,date_format, date_format_2,new_title=None):
    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')

    filtered_data = data[(data['Date'] >= sday) & (data['Date'] <= eday)]

    relative_date,relative_title= date_format_func2(date_format_2)

    filtered_data_2 = filtered_data[filtered_data['Date'] >= (datetime.today()-relative_date)]

    filtered_data['Volatility'] = filtered_data['High'] - filtered_data['Low']
    filtered_data_2['Volatility'] = filtered_data_2['High'] - filtered_data_2['Low']

    average_period = filtered_data_2['Volatility'].mean()
    average = filtered_data['Volatility'].mean()

    
    avg_line_color = check_average(average_period,average)

    filtered_data['Sorting'] = np.where(filtered_data['Volatility'] > average, 'Higher' , 'Lower')
    fig = px.bar(filtered_data, x = 'Date', y = 'Volatility', color = 'Sorting')

    fig.add_hline(y = average, line_color = 'yellow', showlegend = True, name = 'Avg')
    fig.add_hline(y = average_period, line_color = avg_line_color, showlegend = True, name = f'Avg Volatility: {relative_title}', line_dash = 'dash')
    fig.add_shape(type = 'rect',y0 = 0 , x0 = filtered_data_2.iloc[-1]['Date'] , x1 = filtered_data_2.iloc[0]['Date'], y1 = filtered_data['Volatility'].max(),fillcolor="rgba(0,100,80,0.2)", line = dict(width = 0), showlegend = True, name = relative_title)
    fig.update_layout(
    barmode = 'stack',
    dragmode = False,
    title = 'Volatility',
    title_font=dict(size=24, family='Soin Sans Pro', color='white'),
    legend=dict( x=0,  y=0.98, title = None, borderwidth = 0.3, font = dict(size = 12),bgcolor="rgba(0,0,0,0)")
    )

    return fig



def date_format_func(data):
    if data == '3 Months' or data == '6 Months' or data == '1 Year':
        return '%b %Y'
    elif data == '1 Month' or data == '1 Week':
        return '%d/%m/%y'

def date_format_func2(data):
    if data == '6 Months':
        return [relativedelta(months = 6), 'Last 6 Months']
    elif data == '3 Months':
        return [relativedelta(months = 3), 'Last 3 Month']
    elif data == '1 Month':
        return [relativedelta(months = 1), 'Last 1 Month']
    elif data == '1 Week':
        return [relativedelta(weeks = 1 ), 'Last 7 Days']



def first_part():
    
    col1, col2, col3 = st.columns([3,3,3])
    st.markdown("""<style>.fixed-height {height: 325px;  overflow: auto; }</style>""",unsafe_allow_html=True,)
   
    data,name,sector,General_AI_description, sday,eday, date_format = get_data()
    if "_" in sector:
        sector = sector.replace("_", " ")
            
    _,Date_title,AI_description = General_AI_description.split("**")
    
    with col2:
        
        for i in range(0,2):
            st.write(" ")
            st.plotly_chart(line_chart(data[i],name[i],sday,eday, date_format,date_format_2 = None )[0],use_container_width = False, config = {'displayModeBar' : False})
            

    with col1:
        st.markdown(f"<h1 style='font-size: 60px; color: white;'>{sector}</h1>", unsafe_allow_html=True)
        st.markdown(f'**{Date_title}**')
        st.markdown(f"<div class='fixed-height'>{AI_description}</div>",unsafe_allow_html=True)
        st.write(" ")
        st.plotly_chart(line_chart(data[3],name[3],sday,eday, date_format, date_format_2 = None)[0], use_container_width = False, config = {'displayModeBar' : False})  

    with col3:
        for i in range(2,5):
            if i == 3:
                continue
            else:
                st.write(" ")
                st.plotly_chart(line_chart(data[i],name[i],sday,eday, date_format, date_format_2 = None)[0], use_container_width = False, config = {'displayModeBar' : False})
    return name,data,sday,eday,date_format 

def second_part(s3 = s3client, sector = sector):
    name,output_data,sday,eday,date_format  = first_part()

    close_response = s3.get_object(Bucket = 'stocksectordata' , Key = f'{sector}/close_description.json')
    close_data = close_response['Body'].read().decode('utf-8')
    close_data = json.loads(close_data)

    st.header('Explore Stock Details')
    col1,col2 = st.columns(2)
    with col1:
        date_list = ['1 Year', '6 Months', '3 Months', '1 Month', '1 Week']
        cdate_list = date_list.copy().reverse()
        stock_name = st.selectbox('Select a Stock for Detailed Analysis',name)


        date_format_copy = date_format[:]
        try:
            date_format_2 = st.segmented_control('**Select Time Period**', date_list[date_list.index(date_format_copy)+1::], selection_mode = 'single', default = date_list[date_list.index(date_format_copy)+1])
        except IndexError:
            date_format_2 = '1 Week'

        close_description = close_data[f'{stock_name}'][cdate_list.index(date_format_2)]
        st.write(close_description)

        data = output_data[name.index(stock_name)] 
        st.markdown(f"<h1 style='font-size: 45px; color:#fffd7b ;'>{stock_name}</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size: 30px; color: white;'>Period: <span style='color: yellow;'>{date_format.title()} vs. {date_format_2}</span></h1>", unsafe_allow_html=True)
        st.plotly_chart(line_chart(data,sday = sday,eday = eday, date_format = date_format, new_title = f'Price', name = None, add_trendline = True, date_format_2 = date_format_2)[0], use_container_width = True, config = {'displayModeBar' : False})
       
        st.plotly_chart(volatility_chart(data,sday = sday,eday = eday, date_format = date_format, new_title = f'Price', name = None, date_format_2 = date_format_2), use_container_width = True, config = {'displayModeBar' : False})
        
    with col2:
        st.markdown(f"<h1 style='font-size: 100px; color:black ;'>|</h1>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='font-size: 110px; color:black ;'>|</h1>", unsafe_allow_html=True)
        st.plotly_chart(scatter_plot(data,sday = sday,eday = eday, date_format = date_format, new_title = None , name = None, date_format_2 = date_format_2), use_container_width = True, config = {'displayModeBar' : False})
       
second_part()