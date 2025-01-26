import streamlit as st
import boto3
from io import StringIO
import pandas as pd
import plotly.express as px
from datetime import datetime
from dateutil.relativedelta import relativedelta
import numpy as np

st.set_page_config(layout="wide", page_title = "IndusStock Insight")
st.header('**IndusStock Insight**')
st.write("""IndusStock Insights is an AI-powered platform that helps investors make informed decisions by identifying the top 5 stocks in a specific industry. It pulls real-time data through a stock API and uses advanced machine learning to analyze market trends and company performance.
The platform generates interactive charts and provides intelligent recommendations, guiding users on whether to buy, hold, or avoid stocks based on data-driven insights. With its combination of real-time analysis and AI forecasts, IndusStock Insights empowers users to navigate the stock market confidently and optimize their investments.""")


def date_selectbox():
    
    end_date = datetime.now()
    period = st.segmented_control('**Select Time Period**', ['1 Year', '6 Months', '3 Months', '1 Month', '1 Week'], selection_mode = 'single', default = '3 Months')

    if period == '3 Months':

        start_date = end_date - relativedelta(months=3)
        return start_date,end_date,'3_Months_AI_analysis.txt', '3 months'

    elif period == '1 Month':

        start_date = end_date - relativedelta(months=1)
        return start_date,end_date, 'Monthly_AI_analysis.txt', '1 month'

    elif period == '1 Week':

        start_date = end_date - relativedelta(weeks=1)
        return start_date,end_date, 'Weekly_AI_analysis.txt', '1 week'

    elif period == '6 Months':

        start_date = end_date - relativedelta(months = 6)
        return start_date,end_date, '6_Months_AI_analysis.txt', '6 months'

    elif period == '1 Year':

        start_date = end_date - relativedelta(years=1)
        return start_date,end_date, '1_Year_AI_analysis.txt', '1 year'

    

gsday, geday , gAI_description_txt, gdate_format = date_selectbox()

def get_data(sday = gsday, eday = geday, AI_description_txt = gAI_description_txt, date_format = gdate_format):
    
    

    s3 = boto3.client(
        's3',
        aws_access_key_id=st.secrets["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=st.secrets["AWS_SECRET_ACCESS_KEY"],
        region_name=st.secrets.get("AWS_DEFAULT_REGION", "us-east-2")
    )

    response = s3.get_object(Bucket='stocksectordata', Key='sector_list.txt')
    sector_string = response['Body'].read().decode('utf-8')

    sector_list = sector_string.split(', ')

    tags_sector_list = sector_list.copy()
    tags_sector_list[tags_sector_list.index('Real_Estate')] = 'Real Estate'

    
    sector = st.pills('**Tags**', set(tags_sector_list), selection_mode = 'single', default = 'Tech')
    if sector == 'Real Estate':
        sector = 'Real_Estate'

    tables = []
    names = []
    
   

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
    
def line_chart(data,name,sday,eday,date_format,new_title=None, add_trendline = False):
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
    title=name,  
    title_x=0.5,            
    title_font=dict(size=24, family='Soin Sans Pro', color='white'),
    width = 600,
    height = 400,
    xaxis = dict(tickformat = date_format_func(date_format))
)
    if add_trendline == True:
        relative_date,relative_title= date_format_func2(date_format)
        filtered_data_2 = filtered_data[filtered_data['Date'] >= (datetime.today()-relative_date)]
        line_color_2 = check_color(filtered_data_2)
        line_start_date = filtered_data_2.iloc[0]['Date']
        line_start_value = filtered_data_2.iloc[0]['Close']
        line_end_date = filtered_data_2.iloc[-1]['Date']
        line_end_value = filtered_data_2.iloc[-1]['Close']

        fig.add_shape(type = 'line', x0 = line_start_date, y0 = line_start_value, x1 = line_end_date, y1 = line_end_value, line = dict(color = line_color_2, width = 2, dash = 'dash'), showlegend = True, name = 'Close: ' + relative_title)

    

    return [fig,line_color]


def scatter_plot(data,name,sday,eday,date_format,new_title=None):

    data['Date'] = pd.to_datetime(data['Date'], format='%m/%d/%Y')
    filtered_data = data[(data['Date'] >= sday) & (data['Date'] <= eday)]
    relative_date,relative_title = date_format_func2(date_format)
    filtered_data['Highlight'] = np.where(filtered_data['Date'] >= (datetime.today()-relative_date),relative_title, 'Older')
    filtered_data['Volume_Period'] = np.where(filtered_data['Date'] >= (datetime.today()-relative_date),filtered_data['Volume'], np.nan)

    average_period = filtered_data['Volume_Period'].mean()

    average = filtered_data['Volume'].mean()
    
    def check_average(average_period,average):
        if average_period > average:
            avg_line_color = '#40FF00'
            return avg_line_color
        else:
            avg_line_color = '#FF2800'
            return avg_line_color

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
     legend=dict( x=0.75,  y=0.98, title = None, borderwidth = 0.3)
)

    return fig




def date_format_func(data):
    if data == '3 months' or data == '6 months' or data == '1 year':
        return '%b %Y'
    elif data == '1 month' or data == '1 week':
        return '%d/%m/%y'

def date_format_func2(data):
    if data == '1 year':
        return [relativedelta(months = 6), 'Last 6 Months']
    elif data == '6 months':
        return [relativedelta(months = 3), 'Last 3 Month']
    elif data == '3 months':
        return [relativedelta(months = 1), 'Last 1 Month']
    elif data == '1 month' or data == '1 week':
        return [relativedelta(weeks = 1 ), 'Last 7 Days']



def first_part():
    
    col1, col2, col3 = st.columns([3,3,3])
    st.markdown("""<style>.fixed-height {height: 325px;  overflow: auto; }</style>""",unsafe_allow_html=True,)
   
    data,name,sector,AI_description, sday,eday, date_format = get_data()
    if "_" in sector:
        sector = sector.replace("_", " ")
            

    with col2:
        
        for i in range(0,2):
            st.write(" ")
            st.plotly_chart(line_chart(data[i],name[i],sday,eday, date_format)[0],use_container_width = False, config = {'displayModeBar' : False})
            

    with col1:
        st.markdown(f"<h1 style='font-size: 60px; color: white;'>{sector}</h1>", unsafe_allow_html=True)
        st.markdown(f"<div class='fixed-height'>{AI_description}</div>",unsafe_allow_html=True)
        st.write(" ")
        st.plotly_chart(line_chart(data[3],name[3],sday,eday, date_format)[0], use_container_width = False, config = {'displayModeBar' : False})  

    with col3:
        for i in range(2,5):
            if i == 3:
                continue
            else:
                st.write(" ")
                st.plotly_chart(line_chart(data[i],name[i],sday,eday, date_format)[0], use_container_width = False, config = {'displayModeBar' : False})
    return name,data,sday,eday,date_format 

def second_part():
    
    name,output_data,sday,eday,date_format  = first_part()
    st.header('Explore Stock Details')
    col1,col2 = st.columns(2)
    with col1:
        stock_name = st.selectbox('Select a Stock for Detailed Analysis',name)
        data = output_data[name.index(stock_name)]
        st.markdown(f"<h1 style='font-size: 45px; color: white;'>{stock_name}</h1>", unsafe_allow_html=True)
        st.plotly_chart(line_chart(data,sday = sday,eday = eday, date_format = date_format, new_title = f'Price', name = None, add_trendline = True)[0], use_container_width = True, config = {'displayModeBar' : False})
        st.plotly_chart(scatter_plot(data,sday = sday,eday = eday, date_format = date_format, new_title = None , name = None), use_container_width = True, config = {'displayModeBar' : False})
second_part()