
import requests
import boto3
from io import StringIO
import os

from openai import OpenAI
def trend_stock_sector():
    AI_api = os.getenv('AI_api_key')
    base_URL = "https://api.deepseek.com"
    client = OpenAI(api_key = AI_api, base_url = base_URL)
    response = client.chat.completions.create(
        model = 'deepseek-chat',
        messages = [
            {'role' : 'system' , 'content' : "output top 5 stock symbol for Tech, Healthcare, Financials, Energy , Industrials, Real_Esstate sector in the US. Just the symbol on the same line not extra, external information, go to another line for each sector and always use the given sector as lable"},
            {'role' : 'user' , 'content' : ''}],
        stream = False,
        max_tokens = 200)
    return response.choices[0].message.content
    


def get_stock_data(symbol):
    
    #API_INFO
    api_key = os.getenv('Stock_API')
    base_url = 'https://api.twelvedata.com/time_series'
    params = { 'interval' : '1day', 'outputsize' : '100' , 'symbol' : f'{symbol}' , 'timezone' : 'EST'
              , 'outputsize' : '100' , 'apikey' : api_key}

    try:
        response = requests.get(base_url,params)
        if response.status_code == 200:
            data = response.json()
            return [data['meta']['symbol'], data['values']]
    except requests.RequestException as r:
        print('ERROR: ', r)
        return None


from datetime import datetime

def change_format(data):
    result = []
    for i in data[1]:
        output = {}
        original_datetime = datetime.strptime(i['datetime'],'%Y-%m-%d')
        output['Date'] = original_datetime.strftime('%m/%d/%Y')
        output['Open'] = float(i['open'])
        output['High'] = round(float(i['high']),2)
        output['Low'] = round(float(i['low']),2)
        output['Close'] = round(float(i['close']),2)
        output['Volume'] = int(i['volume'])
        result.append(output)
    return result

def calculation(values_cal):
        one_week_ago = (datetime.now() - relativedelta(days = 7)).date()
        elist1 = []
    
        for i in range(1,7):
                elist1.append(values_cal[i]['Close'])
                
        average1 = sum(elist1)/len(elist1)
        average2 = values_cal[0]['Close']
        return [(average2 - average1)/average1, one_week_ago]

import time
import csv
import json
from dateutil.relativedelta import relativedelta

def import_top_5():
    trend_stock = trend_stock_sector().split('\n')
    s3 = boto3.client('s3')
    sector_list = []
    description_list = []
    for i in trend_stock:

        count = 0
        sector,stock = i.split(":")
        sector_list.append(sector)

        for j in stock.split():

            count+=1
            stock_values = change_format(get_stock_data(j))
            
            average, one_week_ago = calculation(stock_values)
        
            average_description = f'{j} stock price since {one_week_ago}: {round(average*100,2)} %'
            description_list.append(average_description)
              
            time.sleep(10)

            csv_buffer = StringIO()
            writer = csv.DictWriter(csv_buffer, fieldnames=stock_values[0].keys())
            writer.writeheader()
            writer.writerows(stock_values)

            s3.put_object(Bucket='stocksectordata', Key=f'{sector}/Data/stock_{count}.csv', Body=csv_buffer.getvalue())
            s3.put_object(Bucket='stocksectordata', Key=f'{sector}/Name/stock_{count}_name.txt', Body= str(j) )

        s3.put_object(Bucket='stocksectordata', Key=f'{sector}/Description.txt', Body= ', '.join(description_list))

    s3.put_object(Bucket='stocksectordata', Key=f'sector_list.txt', Body=', '.join(sector_list))        

def lambda_handler(event, context):
    import_top_5()


