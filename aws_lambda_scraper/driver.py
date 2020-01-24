from bs4 import BeautifulSoup
from selenium import webdriver
import os
import re
import json
import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError
from crawl import crawl_site

# Scraping all
# The format used for AWS lambda functions
def perform_scrape(event=None, context=None):

    # defining the chrome webdriver for selenium
    chrome_options = webdriver.ChromeOptions()
    # Adding headless chrome
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    #chrome_options.add_argument('--window-size=1280x1696')
    chrome_options.add_argument('--no-sandbox')
    #chrome_options.add_argument('--hide-scrollbars')
    #chrome_options.add_argument('--enable-logging')
    #chrome_options.add_argument('--log-level=0')
    #chrome_options.add_argument('--v=99')
    #chrome_options.add_argument('--single-process')
    chrome_options.add_argument('--ignore-certificate-errors')

    # chrome_options.binary_location = os.getcwd() + "/headless-chromium"
    # driver = webdriver.Chrome(os.getcwd() + "/chromedriver",chrome_options=chrome_options)

    driver = webdriver.Chrome(chrome_options=chrome_options)

    # hashtable to store the internship openings
    open_internships = {}

    # Establishing connection with dynamodb & companies table

    dynamodb = boto3.resource('dynamodb')
    company_table = dynamodb.Table('companies')

    # Retrieving all the companies in the table

    try:
        response = company_table.scan()
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        company_list = response['Items']

    # Cycling through the items in the table, running the scrape algos

    for company in company_list:

        results = crawl_site(company['url'], company['function'], driver)

        if (results is not None) and (len(results) > 0):
            open_internships[company['company-name']] = results

    driver.quit()

    return {
        'statusCode': 200,
        'body': json.dumps(open_internships)
    }

if __name__ == "__main__":
    print(perform_scrape())
