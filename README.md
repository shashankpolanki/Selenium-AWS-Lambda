# Selenium-AWS-Lambda
In the project I run a selenium-based web scraper using serverless AWS lambda functions. The purpose of the project was to scrape company websites for internship opportunities once a day using a cloudwatch event as a trigger; however, the code here could also be used as a reference on how to deploy selenium as a serverless lambda function to do periodic jobs like data-scraping and automation work.

In order to deploy the code in a lambda environment, zip up the aws-lambda-scraper directory in a unix environment and deploy as a AWS lambda function. 
