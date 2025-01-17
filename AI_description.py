import boto3
from openai import OpenAI
import os
def get_sector():
    s3 = boto3.client('s3')
    sector_list = s3.get_object(Bucket='stocksectordata', Key='sector_list.txt')
    return(sector_list['Body'].read().decode('utf-8'))

def output_data():
    sector_list = get_sector().split(', ')
    print(sector_list)
    s3 = boto3.client('s3')
    for sector in sector_list:
        
        description = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Description.txt')
        description = description['Body'].read().decode('utf-8')
        AI_description = AI_analysis(description)
        s3.put_object(Bucket='stocksectordata', Key=f'{sector}/AI_analysis.txt', Body=AI_description)
            

def AI_analysis(average_description_list):
    average_description = ", ".join(average_description_list)
    AI_api_key = os.getenv('AI_api_key')
    base_URL = "https://api.deepseek.com"
    client = OpenAI(api_key = AI_api_key, base_url = base_URL)
    response = client.chat.completions.create(
        model = 'deepseek-chat',
        messages = [
            {'role' : 'system' , 'content' : "You are professional stock analyzer based on the current world's situation, keep your analysis short(3-4) sentence but comprehensive, analytical, professional, then advice user should invest in a specific stock in the provided industry or not. Keep everything in 1 paragraph"},
            {'role' : 'user' , 'content' : f'{average_description}'}],
        stream = False,
        max_tokens = 250)
    return response.choices[0].message.content

def lambda_handler(context=None, event=None):
    output_data()


            