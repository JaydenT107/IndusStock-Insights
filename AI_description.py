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
        
        weekly_description = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Description/Weekly_Description.txt')
        wdescription = weekly_description['Body'].read().decode('utf-8')
        WAI_description = AI_analysis(wdescription, sector)
        s3.put_object(Bucket='stocksectordata', Key=f'{sector}/AI_Description/Weekly_AI_analysis.txt', Body=WAI_description)
            
        monthly_description = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Description/Monthly_Description.txt')
        mdescription = monthly_description['Body'].read().decode('utf-8')
        MAI_description = AI_analysis(mdescription, sector)
        s3.put_object(Bucket='stocksectordata', Key=f'{sector}/AI_Description/Monthly_AI_analysis.txt', Body=MAI_description)    

        threemonth_description = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Description/3_months_Description.txt')
        threemdescription = threemonth_description['Body'].read().decode('utf-8')
        TMAI_description = AI_analysis(threemdescription, sector)
        s3.put_object(Bucket='stocksectordata', Key=f'{sector}/AI_Description/3_Months_AI_analysis.txt', Body=TMAI_description)

        
        sixmonth_description = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Description/6_months_Description.txt')
        sixmdescription = sixmonth_description['Body'].read().decode('utf-8')
        SMAI_description = AI_analysis(sixmdescription, sector)
        s3.put_object(Bucket='stocksectordata', Key=f'{sector}/AI_Description/6_Months_AI_analysis.txt', Body=SMAI_description)
        
        oneyear_description = s3.get_object(Bucket='stocksectordata', Key=f'{sector}/Description/1_year_Description.txt')
        oneydescription = oneyear_description['Body'].read().decode('utf-8')
        OYAI_description = AI_analysis(oneydescription, sector)
        s3.put_object(Bucket='stocksectordata', Key=f'{sector}/AI_Description/1_Year_AI_analysis.txt', Body=OYAI_description)

def AI_analysis(average_description_list, sector):
    average_description = ", ".join(average_description_list)
    AI_api_key = os.getenv('AI_api_key')
    base_URL = "https://api.deepseek.com"
    client = OpenAI(api_key = AI_api_key, base_url = base_URL)
    response = client.chat.completions.create(
        model = 'deepseek-chat',
        messages = [
            {'role' : 'system' , 'content' : f"You are professional stock analyzer based on the current world's situation and provided information to analyze the current state of the {sector} industry based on the performance of its top 5 stocks over the provided period, keep your analysis short(3-4) sentence but comprehensive, analytical, professional, general, don't include number . Keep everything in 1 paragraph"},
            {'role' : 'user' , 'content' : f'{average_description}'}],
        stream = False,
        max_tokens = 250)
    return response.choices[0].message.content

def lambda_handler(context=None, event=None):
    output_data()


            
